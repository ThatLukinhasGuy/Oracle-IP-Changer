import customtkinter as ctk
import oci
from oci.core.models import CreateVnicDetails

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

appWidth, appHeight = 265, 465

def delete_ip(self):
    config = oci.config.from_file(file_location="config.json")
    compartment_id = self.comp_ocid.get()
    instance_id = self.vm_ocid.get()
    vnic_display_name = "dududini"
    vcn_client = oci.core.VirtualNetworkClient(config)
    ephemeral_ips = vcn_client.list_public_ips(
        scope="AVAILABILITY_DOMAIN",
        availability_domain=self.ad_name.get(),
        lifetime="EPHEMERAL",
        compartment_id=compartment_id,
    ).data

    for ephemeral_ip in ephemeral_ips:
        vcn_client.delete_public_ip(public_ip_id=ephemeral_ip.id)

def create_reserved_ip(vcn_client, compartment_id, self):
    compartment_id = self.comp_ocid.get()
    instance_id = self.vm_ocid.get()
    vnic_display_name = "dududini"
    config = oci.config.from_file(file_location="config.json")
    vcn_client = oci.core.VirtualNetworkClient(config)
    create_ip_details = oci.core.models.CreatePublicIpDetails(
        compartment_id=compartment_id,
        display_name="New Reserved IP",
        lifetime="EPHEMERAL",
        private_ip_id=self.ip_ocid.get(),
    )

    new_reserved_ip = vcn_client.create_public_ip(create_public_ip_details=create_ip_details).data
    return new_reserved_ip

def attach_ip_to_vm(virtual_network, compute_client, instance_id, reserved_ip_id, vnic_display_name, self):
    compartment_id = self.comp_ocid.get()
    instance_id = self.vm_ocid.get()
    vnic_display_name = "dududini"
    config = oci.config.from_file(file_location="config.json")
    vcn_client = oci.core.VirtualNetworkClient(config)
    reserved_ips = vcn_client.list_public_ips(
        scope="REGION",
        lifetime="EPHEMERAL",
        compartment_id=compartment_id,
    ).data
    update_ip_details = oci.core.models.UpdatePublicIpDetails(
        display_name="New Reserved IP",
        private_ip_id=self.ip_ocid.get(),
    )
    for reserved_ip in reserved_ips:
        p = oci.core.VirtualNetworkClient(config)
        p.update_public_ip(update_public_ip_details=update_ip_details,public_ip_id=reserved_ip.id)

class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
 
        self.title("Oracle Cloud IP Changer")
        self.geometry(f"{appWidth}x{appHeight}")
        self.resizable(0, 0)

        self.label = ctk.CTkLabel(self, text="OCI IP Changer", font=("roboto", 20))
        self.label.grid(row=0, column=0, columnspan=1, padx=10, pady=10, sticky="ew")

        self.ip_ocid = ctk.CTkEntry(self, placeholder_text="Private IP OCID", width=250, height=25)
        self.ip_ocid.grid(row=1, column=0, columnspan=1, padx=7, pady=7, sticky="ew")
        
        self.ad_name = ctk.CTkEntry(self, placeholder_text="Availability Domain", width=250, height=25)
        self.ad_name.grid(row=2, column=0, columnspan=1, padx=7, pady=7, sticky="ew")

        self.vm_ocid = ctk.CTkEntry(self, placeholder_text="Virtual Machine OCID", width=250, height=25)
        self.vm_ocid.grid(row=3, column=0, columnspan=1, padx=7, pady=7, sticky="ew")

        self.comp_ocid = ctk.CTkEntry(self, placeholder_text="Compartment OCID", width=250, height=25)
        self.comp_ocid.grid(row=4, column=0, columnspan=1, padx=7, pady=7, sticky="ew")

        self.vm_name = ctk.CTkEntry(self, placeholder_text="Virtual Machine Name", width=250, height=25)
        self.vm_name.grid(row=5, column=0, columnspan=1, padx=7, pady=7, sticky="ew")

        self.change_ip_button = ctk.CTkButton(self, text="Change IP", command=self.change_ip)
        self.change_ip_button.grid(row=6, column=0, padx=20, pady=20, sticky="ew")

        self.displayBox = ctk.CTkTextbox(self, width=225, height=115)
        self.displayBox.grid(row=7, column=0, columnspan=4, padx=20, pady=20, sticky="nsew")

    def change_ip(self):
        compartment_id = self.comp_ocid.get()
        instance_id = self.vm_ocid.get()
        vnic_display_name = "dududini"
        display_name = self.vm_name.get()
        config = oci.config.from_file(file_location="config.json")
        identity = oci.identity.IdentityClient(config)
        user = identity.get_user(config["user"]).data
        instances = oci.core.ComputeClient(config).list_instances(
            compartment_id=user.compartment_id).data
        instance_id = {i.display_name: i.id for i in instances}[display_name]
        compute_client = oci.core.ComputeClient(config)
        vnic_data = compute_client.list_vnic_attachments(
            compartment_id=user.compartment_id, instance_id=instance_id).data
        vcn_client = oci.core.VirtualNetworkClient(config)
        deleteip = delete_ip(self)
        try:
            new_reserved_ip = create_reserved_ip(vcn_client, compartment_id, self)
            attach_ip = attach_ip_to_vm(vcn_client, compute_client, instance_id, new_reserved_ip.id, vnic_display_name, self)
            vnic_list = [vcn_client.get_vnic(vnic_attachment.vnic_id).data
                         for vnic_attachment in vnic_data]
        except oci.exceptions.ServiceError as e:
            if e.status == 200:
                pass
            else:
                error = f"The operation finished with a error.\nError code: {e.status}"
                self.displayBox.delete("0.0", "200.0")
                self.displayBox.insert("0.0", error)
        public_ip = {i.display_name: i.public_ip for i in vnic_list}[display_name]
        text = f"New IP: {public_ip}"
        self.displayBox.delete("0.0", "200.0")
        self.displayBox.insert("0.0", text)
if __name__ == "__main__":
    app = App()
    # Used to run the application
    app.mainloop()

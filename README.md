# Oracle IP Changer
IP Changer for Oracle Cloud for VMs.

## How to use
1. Download or clone the repository.
2. Run `pip install -r requirements.txt` to install the dependencies.
3. Generate an API key on the Oracle Cloud web page and download the private key (must be named **key.pem**).
4. Create a config.json file with the following syntax:

```
[DEFAULT]
user=<user>
fingerprint=<fingerprint>
tenancy=<tenancy>
region=<region>
key_file=key.pem
```

5. Run the **IP_Changer.pyw** file.
6. Fill in the necessary information.
7. Done.

## TO-DO
- [x] Create an error output. For now, rename the file to **IP_Changer.py** and see the error code.
- [x] Webhook support

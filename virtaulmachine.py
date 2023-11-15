from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
import os

print(f"Provisioning a virtual machine in Azure using Python.")

# Acquire credential object using CLI-based authentication.
credential = AzureCliCredential()

# Retrieve subscription ID from environment variable.
subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"] = "1196ed17-0b51-48be-bd51-ed701b1c95e0"

# 1 - create a resource group

# Get the management object for resources, this uses the credentials from the CLI login.
resource_client = ResourceManagementClient(credential, subscription_id)

# Set constants we need in multiple places.  You can change these values however you want.
RESOURCE_GROUP_NAME = "scriptGroup"
LOCATION = "westeurope"

# create the resource group.
rg_result = resource_client.resource_groups.create_or_update(RESOURCE_GROUP_NAME,
    {
        "location": LOCATION
    }
)

print(f"Provisioned resource group {rg_result.name} in the {rg_result.location} region")

# 2 - provision the virtual network

# A virtual machine requires a network interface client (NIC). A NIC requires a virtual network (VNET) and subnet along with an IP address.  
# To support this requirement, we need to provision the VNET and Subnet first, then provision the NIC.

# Network and IP address names
VNET_NAME = "scriptNet"
SUBNET_NAME = "scriptSnet"
IP_NAME = "scriptIp"
IP_CONFIG_NAME = "ipconfig1"
NIC_NAME = "scriptNic"

# Get the management object for the network
network_client = NetworkManagementClient(credential, subscription_id)

# Create the virtual network
poller = network_client.virtual_networks.begin_create_or_update(RESOURCE_GROUP_NAME,
    VNET_NAME,
    {
    "properties": {
        "addressSpace": {
        "addressPrefixes": [
            "10.0.0.0/16"
        ]
        },
        "flowTimeoutInMinutes": 10
    },
    "location": "westeurope"
    }
)

vnet_result = poller.result()

print(f"Provisioned virtual network {vnet_result.name} with address prefixes {vnet_result.address_space.address_prefixes}")

# 3 - Create the subnet
poller = network_client.subnets.begin_create_or_update(RESOURCE_GROUP_NAME,
    VNET_NAME, SUBNET_NAME,
    { "properties": { "addressPrefix": "10.0.0.0/16" } }
)
subnet_result = poller.result()

print(f"Provisioned virtual subnet {subnet_result.name} with address prefix {subnet_result.address_prefix}")

# 4 - Create the IP address
poller = network_client.public_ip_addresses.begin_create_or_update(RESOURCE_GROUP_NAME,
    IP_NAME,
    {
        "location": LOCATION,
        "sku": { "name": "Standard" },
        "public_ip_allocation_method": "Static",
        "public_ip_address_version" : "IPV4"
    }
)

# 5 - Create the network interface client
poller = network_client.network_interfaces.begin_create_or_update(RESOURCE_GROUP_NAME,
    NIC_NAME,
    {  
    "properties": {  
    "ipConfigurations": [  
        {  
            "name": "ipconfig1",  
            "properties": {  
            "publicIPAddress": {  
            "id": "/subscriptions/1196ed17-0b51-48be-bd51-ed701b1c95e0/resourceGroups/scriptGroup/providers/Microsoft.Network/publicIPAddresses/scriptIp"  
            },  
            "subnet": {  
            "id": "/subscriptions/1196ed17-0b51-48be-bd51-ed701b1c95e0/resourceGroups/scriptGroup/providers/Microsoft.Network/virtualNetworks/scriptNet/subnets/scriptSnet"  
            }  
            }  
        }  
    ]  },  
    "location": "westeurope"  
    }
)

ip_address_result = poller.result()


nic_result = poller.result()

print(f"Provisioned network interface client {nic_result.name}")

# 6 - Create the virtual machine

# Get the management object for virtual machines
compute_client = ComputeManagementClient(credential, subscription_id)

VM_NAME = "scriptVM"
USERNAME = "ben"
PASSWORD = "ben"

print(f"Provisioning virtual machine {VM_NAME}; this operation might take a few minutes.")

# Create the VM (Ubuntu 18.04 VM)
# on a Standard DS1 v2 plan with a public IP address and a default virtual network/subnet.

poller = compute_client.virtual_machines.begin_create_or_update(RESOURCE_GROUP_NAME, VM_NAME,
    {  
    "id": "/subscriptions/1196ed17-0b51-48be-bd51-ed701b1c95e0/resourceGroups/scriptGroup/ providers/Microsoft.Compute/virtualMachines/vm4",  
    "type": "Microsoft.Compute/virtualMachines",  
    "properties": {  
    "osProfile": {  
    "adminUsername": "ben",  
    "secrets": [  
        
    ],  
    "computerName": "scriptVM",  
    "linuxConfiguration": {  
        "ssh": {  
        "publicKeys": [  
        {  
        "path": "/home/ben/.ssh/authorized_keys",  
        "keyData": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDFADdQcHQDdoXF9Wk7UnFO9KO9ecxjjG/WqseFxtFay+3IbaJCiwHRJVW9Rj+nj3IMJWbJkGfSEkp9BdKrMYv07EkOQtz8+Sn7f1/l3XnO/3gBdj7OqksYil+J8WpZrNc60yzxczLJCQK5+pJUNKIrNIJtewoWy9I0neKkl4XrETn1SguqCeoMksOzkYqk4CRXbNlX7CGw9XoosvA+KFtk1im429QswYM5voPlKJqsOo6lVvO9KhYAJpxkgxzEVolC31N2pvPtKmqhBS98Ut/AXloB90jXSnJ/9tibnliKwqecnaHpyyG3MsdtKVeG+aQGQGM2mRUpXB5T/yeALa5lxxuCSPrOI6e9sYwHWPfkVB6m0IbGngOcU9oaQNPQJoWVUDTTIC8nlx3JT3ZmpD/zkUf4NE6Jcc848/YORifzVUbNE85T3d1ayuFGdcCScnPFHMvX7SpRYUDCm0iqiFOrCQzg4VK6GupqfU5+z8LOHyFsXz1Yeo1rzjoKU9EcNgU= bendavcorr@instance-1 "  
        }  
        ]  
        },  
        "disablePasswordAuthentication": "true"  
    }  
    },  
    "networkProfile": {  
    "networkInterfaces": [  
        {  
        "id": "/subscriptions/1196ed17-0b51-48be-bd51-ed701b1c95e0/resourceGroups/scriptGroup/ providers/Microsoft.Network/networkInterfaces/scriptNic",  
        "properties": {  
        "primary": "true" 
        }  
        }  
    ]  
    },  
    "storageProfile": {  
    "imageReference": {  
        "sku": "16.04-LTS",  
        "publisher": "Canonical",  
        "version": "latest",  
        "offer": "UbuntuServer"  
    },  
    "dataDisks": [  
        
    ]  
    },  
    "hardwareProfile": {  
    "vmSize": "Standard_D1_v2"  
    },  
    "provisioningState": "Creating"  
    },  
    "name": "scriptVM",  
    "location": "westeurope"  
    }
)

vm_result = poller.result()

print(f"Provisioned virtual machine {vm_result.name}")
from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import uuid
from datetime import datetime


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class PortConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    switch_number: int
    port_type: str
    port_name: str
    config_type: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PortConfigCreate(BaseModel):
    switch_number: int
    port_type: str
    port_name: str
    config_type: str
    description: Optional[str] = None

class PortConfigUpdate(BaseModel):
    config_type: str
    description: Optional[str] = None


# Cisco Configuration Templates
def generate_port_config(port_name: str, config_type: str) -> str:
    """Generate Cisco configuration for a specific port and config type"""
    
    lines = []
    
    # Reset type - special handling (no default)
    if config_type == 'reset':
        lines.append(f"interface {port_name}")
        lines.append("shutdown")
        lines.append("no shutdown")
        lines.append("exit")
        lines.append("!")
        return "\n".join(lines)
    
    # All other types start with default interface
    if config_type != 'none':
        lines.append(f"default interface {port_name}")
        lines.append(f"interface {port_name}")
    
    if config_type == 'data_voice':
        lines.extend([
            "description // Data and Voice //",
            "switchport mode access",
            "switchport access vlan 6",
            "switchport voice vlan 4",
            "auto qos voip cisco-phone",
            "switchport port-security",
            "switchport port-security maximum 3",
            "switchport port-security violation restrict",
            "switchport port-security aging time 1",
            "switchport port-security aging type inactivity",
            "switchport nonegotiate",
            "ip dhcp snooping limit rate 15",
            "ip arp inspection limit rate 15",
            "spanning-tree portfast",
            "spanning-tree bpduguard enable",
            "device-tracking attach-policy MERAKI_POLICY",
            "ip flow monitor MERAKI_AVC_IPV4 input",
            "ip flow monitor MERAKI_AVC_IPV4 output",
            "ipv6 flow monitor MERAKI_AVC_IPV6 input",
            "ipv6 flow monitor MERAKI_AVC_IPV6 output",
            "shutdown",
            "no shutdown",
            "exit"
        ])
    
    elif config_type == 'camera':
        lines.extend([
            "description // Camera //",
            "switchport mode access",
            "switchport access vlan 5",
            "spanning-tree portfast",
            "device-tracking attach-policy MERAKI_POLICY",
            "ip flow monitor MERAKI_AVC_IPV4 input",
            "ip flow monitor MERAKI_AVC_IPV4 output",
            "ipv6 flow monitor MERAKI_AVC_IPV6 input",
            "ipv6 flow monitor MERAKI_AVC_IPV6 output",
            "shutdown",
            "no shutdown",
            "exit"
        ])
    
    elif config_type == 'trunk_wap':
        lines.extend([
            "description // TrunkportforWAP //",
            "switchport mode trunk",
            "switchport trunk native vlan 25",
            "switchport trunk allowed vlan 25,4,8,16,20,30,32",
            "switchport nonegotiate",
            "ip dhcp snooping trust",
            "ip arp inspection trust",
            "device-tracking attach-policy MERAKI_POLICY",
            "ip flow monitor MERAKI_AVC_IPV4 input",
            "ip flow monitor MERAKI_AVC_IPV4 output",
            "ipv6 flow monitor MERAKI_AVC_IPV6 input",
            "ipv6 flow monitor MERAKI_AVC_IPV6 output",
            "shutdown",
            "no shutdown",
            "exit"
        ])
    
    elif config_type == 'vape_sensor':
        lines.extend([
            "description // Vape_Sensor //",
            "switchport mode access",
            "switchport access vlan 30",
            "spanning-tree portfast",
            "device-tracking attach-policy MERAKI_POLICY",
            "ip flow monitor MERAKI_AVC_IPV4 input",
            "ip flow monitor MERAKI_AVC_IPV4 output",
            "ipv6 flow monitor MERAKI_AVC_IPV6 input",
            "ipv6 flow monitor MERAKI_AVC_IPV6 output",
            "shutdown",
            "no shutdown",
            "exit"
        ])
    
    elif config_type == 'trunk_switch':
        lines.extend([
            "description // TrunkportforSwitch //",
            "switchport mode trunk",
            "switchport nonegotiate",
            "ip dhcp snooping trust",
            "ip arp inspection trust",
            "device-tracking attach-policy MERAKI_POLICY",
            "ip flow monitor MERAKI_AVC_IPV4 input",
            "ip flow monitor MERAKI_AVC_IPV4 output",
            "ipv6 flow monitor MERAKI_AVC_IPV6 input",
            "ipv6 flow monitor MERAKI_AVC_IPV6 output",
            "shutdown",
            "no shutdown",
            "exit"
        ])
    
    elif config_type == 'door_system':
        lines.extend([
            "description // DoorSystem //",
            "switchport mode access",
            "switchport access vlan 30",
            "spanning-tree portfast",
            "device-tracking attach-policy MERAKI_POLICY",
            "ip flow monitor MERAKI_AVC_IPV4 input",
            "ip flow monitor MERAKI_AVC_IPV4 output",
            "ipv6 flow monitor MERAKI_AVC_IPV6 input",
            "ipv6 flow monitor MERAKI_AVC_IPV6 output"
        ])
    
    elif config_type == 'algo_bell':
        lines.extend([
            "description // Algo 8301 IP Paging //",
            "switchport access vlan 6",
            "switchport mode access",
            "device-tracking attach-policy MERAKI_POLICY",
            "ip flow monitor IPv4_NETFLOW input",
            "ip flow monitor MERAKI_AVC_IPV4 output",
            "ipv6 flow monitor MERAKI_AVC_IPV6 input",
            "ipv6 flow monitor MERAKI_AVC_IPV6 output",
            "spanning-tree portfast"
        ])
    
    elif config_type == 'voip_server':
        lines.extend([
            "description // VoIP_Server //",
            "switchport mode trunk",
            "switchport trunk allowed vlan 250,4",
            "spanning-tree portfast",
            "ip dhcp snooping trust",
            "ip arp inspection trust",
            "device-tracking attach-policy MERAKI_POLICY",
            "ip flow monitor MERAKI_AVC_IPV4 input",
            "ip flow monitor MERAKI_AVC_IPV4 output",
            "ipv6 flow monitor MERAKI_AVC_IPV6 input",
            "ipv6 flow monitor MERAKI_AVC_IPV6 output",
            "shutdown",
            "no shutdown",
            "exit"
        ])
    
    elif config_type == 'camera_server':
        lines.extend([
            "description // NVR Server //",
            "switchport access vlan 5",
            "switchport mode access",
            "ip dhcp snooping trust",
            "ip arp inspection trust",
            "spanning-tree portfast",
            "device-tracking attach-policy MERAKI_POLICY",
            "ip flow monitor MERAKI_AVC_IPV4 input",
            "ip flow monitor MERAKI_AVC_IPV4 output",
            "ipv6 flow monitor MERAKI_AVC_IPV6 input",
            "ipv6 flow monitor MERAKI_AVC_IPV6 output"
        ])
    
    elif config_type == 'student_vlan8':
        lines.extend([
            "description // Student_VLAN //",
            "switchport mode access",
            "switchport access vlan 8",
            "switchport voice vlan 4",
            "auto qos voip cisco-phone",
            "switchport port-security",
            "switchport port-security maximum 3",
            "switchport port-security violation restrict",
            "switchport port-security aging time 1",
            "switchport port-security aging type inactivity",
            "switchport nonegotiate",
            "ip dhcp snooping limit rate 15",
            "ip arp inspection limit rate 15",
            "spanning-tree portfast",
            "spanning-tree bpduguard enable",
            "device-tracking attach-policy MERAKI_POLICY",
            "ip flow monitor MERAKI_AVC_IPV4 input",
            "ip flow monitor MERAKI_AVC_IPV4 output",
            "ipv6 flow monitor MERAKI_AVC_IPV6 input",
            "ipv6 flow monitor MERAKI_AVC_IPV6 output",
            "shutdown",
            "no shutdown",
            "exit"
        ])
    
    elif config_type == 'printer':
        lines.extend([
            "description // Printer //",
            "switchport mode access",
            "switchport access vlan 6",
            "ip dhcp snooping trust",
            "ip arp inspection trust",
            "switchport voice vlan 4",
            "auto qos voip cisco-phone",
            "spanning-tree portfast",
            "device-tracking attach-policy MERAKI_POLICY",
            "ip flow monitor MERAKI_AVC_IPV4 input",
            "ip flow monitor MERAKI_AVC_IPV4 output",
            "ipv6 flow monitor MERAKI_AVC_IPV6 input",
            "ipv6 flow monitor MERAKI_AVC_IPV6 output",
            "shutdown",
            "no shutdown",
            "exit"
        ])
    
    elif config_type == 'management':
        lines.extend([
            "description // Management //",
            "switchport mode access",
            "switchport access vlan 2",
            "ip dhcp snooping trust",
            "ip arp inspection trust",
            "spanning-tree portfast",
            "spanning-tree bpduguard enable",
            "device-tracking attach-policy MERAKI_POLICY",
            "ip flow monitor MERAKI_AVC_IPV4 input",
            "ip flow monitor MERAKI_AVC_IPV4 output",
            "ipv6 flow monitor MERAKI_AVC_IPV6 input",
            "ipv6 flow monitor MERAKI_AVC_IPV6 output"
        ])
    
    elif config_type == 'pos_machine':
        lines.extend([
            "description // POS_Machine //",
            "switchport mode access",
            "switchport access vlan 150",
            "switchport voice vlan 4",
            "device-tracking attach-policy MERAKI_POLICY",
            "ip flow monitor MERAKI_AVC_IPV4 input",
            "ip flow monitor MERAKI_AVC_IPV4 output",
            "ipv6 flow monitor MERAKI_AVC_IPV6 input",
            "ipv6 flow monitor MERAKI_AVC_IPV6 output",
            "shutdown",
            "no shutdown",
            "exit"
        ])
    
    elif config_type == 'hyperv':
        lines.extend([
            "description // Hyper-V //",
            "switchport mode trunk",
            "no switchport trunk allowed vlan",
            "ip dhcp snooping trust",
            "ip arp inspection trust",
            "device-tracking attach-policy MERAKI_POLICY",
            "ip flow monitor MERAKI_AVC_IPV4 input",
            "ip flow monitor MERAKI_AVC_IPV4 output",
            "ipv6 flow monitor MERAKI_AVC_IPV6 input",
            "ipv6 flow monitor MERAKI_AVC_IPV6 output",
            "shutdown",
            "no shutdown",
            "exit"
        ])
    
    return "\n".join(lines)


# API Routes
@api_router.get("/")
async def root():
    return {"message": "Switch Configuration API"}

# Port Configuration Endpoints
@api_router.post("/ports", response_model=PortConfig)
async def create_port_config(port: PortConfigCreate):
    port_dict = port.dict()
    port_obj = PortConfig(**port_dict)
    await db.port_configs.update_one(
        {"port_name": port.port_name, "switch_number": port.switch_number},
        {"$set": port_obj.dict()},
        upsert=True
    )
    return port_obj

@api_router.get("/ports", response_model=List[PortConfig])
async def get_port_configs(switch_number: Optional[int] = None, port_type: Optional[str] = None):
    query = {}
    if switch_number is not None:
        query["switch_number"] = switch_number
    if port_type is not None:
        query["port_type"] = port_type
    # Use projection to optimize query
    projection = {
        "_id": 0,
        "id": 1,
        "switch_number": 1,
        "port_type": 1,
        "port_name": 1,
        "config_type": 1,
        "description": 1,
        "created_at": 1,
        "updated_at": 1
    }
    ports = await db.port_configs.find(query, projection).to_list(1000)
    return [PortConfig(**port) for port in ports]

@api_router.get("/ports/{port_name}")
async def get_port_config(port_name: str, switch_number: int):
    port = await db.port_configs.find_one(
        {"port_name": port_name, "switch_number": switch_number},
        {"_id": 0}
    )
    if port:
        return PortConfig(**port)
    return None

@api_router.put("/ports/{port_name}")
async def update_port_config(port_name: str, switch_number: int, update: PortConfigUpdate):
    update_dict = update.dict()
    update_dict["updated_at"] = datetime.utcnow()
    result = await db.port_configs.update_one(
        {"port_name": port_name, "switch_number": switch_number},
        {"$set": update_dict}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Port not found")
    port = await db.port_configs.find_one(
        {"port_name": port_name, "switch_number": switch_number},
        {"_id": 0}
    )
    return PortConfig(**port)

@api_router.delete("/ports")
async def reset_all_ports(switch_number: Optional[int] = None):
    query = {}
    if switch_number is not None:
        query["switch_number"] = switch_number
    result = await db.port_configs.delete_many(query)
    return {"deleted_count": result.deleted_count}

# Generate Cisco Configuration Code
@api_router.post("/generate-code")
async def generate_cisco_code(switch_number: int, port_type: str):
    # Get port configurations with projection for optimization
    ports = await db.port_configs.find(
        {"switch_number": switch_number, "port_type": port_type},
        {"_id": 0, "port_name": 1, "config_type": 1}
    ).to_list(1000)
    
    if not ports:
        return {"code": "! No configured ports found", "port_count": 0}
    
    code_lines = []
    
    # Generate configuration for each port
    for port in ports:
        if port.get('config_type') == 'none':
            continue
        
        port_config = generate_port_config(port.get('port_name'), port.get('config_type'))
        if port_config:
            code_lines.append(port_config)
            code_lines.append("")  # Empty line between configs
    
    return {"code": "\n".join(code_lines), "port_count": len(ports)}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

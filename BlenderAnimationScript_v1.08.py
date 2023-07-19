import bpy
from bpy.props import EnumProperty
from bpy.types import Operator, Panel
from bpy.utils import register_class, unregister_class

import math
from math import degrees
import numpy as np
import json
from typing import List
from Models.MotorCommand import MotorCommand
import websocket

from threading import Thread
import threading
import time


#Bones name         
Head = ["head", "neck"]         
Arm_Right = ["wrist.r", "elbow.r", "forearm.r", "shoulder.r"]
Arm_Left = ["wrist.l", "elbow.l", "forearm.l", "shoulder.l"]
Press_Chest = ["hip.joint", "press.bottom", "press.top", "spine.2"]
Leg_Right = ["foot.r", "leg.r", "hip.r"]
Leg_Left = ["foot.l", "leg.l", "hip.l"]
#Start position
HeadStartPos = [90.0000161648565, -0.023980894227513937]
ArmRightStartPos = [176.27359040158078, 176.27359040158078, 89.99940827802038, 90.0]
ArmLeftStartPos = [176.27359040158078, 176.27359040158078, 89.99938778745286, 90.0]
PressStartPos = [0.3127866720913092, 8.089176595380046, 168.89941764531153, -0.1909889112024303]
LegRightStartPos = [110.47904065519744, 131.22145773050158, -31.7]
LegLeftStartPos = [110.47904065519744, 131.22145773050158, -31.7]

status = 'NO'
                 
class Conection_PT_Panel(Panel):

    
    bl_idname = 'Conection_PT_Panel'
    bl_label = 'Conection'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Conection'
          
    def draw(self, context):
        layout = self.layout
        
        #layout.label(text = status, icon = 'X')
               
        layout.operator('connection.connection_op', text ='Connect', icon = 'MOD_WAVE').action = 'CONNECT'
        layout.operator('connection.connection_op', text ='Disconnect', icon = 'X').action = 'DISCONNECT'
        layout.operator('connection.connection_op', text ='Rec', icon = 'REC').action = 'REC'
        layout.operator('connection.connection_op', text ='Pause', icon = 'PAUSE').action = 'PAUSE'
        layout.operator('connection.connection_op', text ='Stop', icon = 'SNAP_FACE').action = 'SNAP_FACE'

class Status_OT_Panel(Operator):
    
    bl_idname = 'connection.connection_op'
    bl_label = 'Connection'
    bl_description = 'Connection'
    bl_options = {'REGISTER', 'UNDO'}

    
 
    action: EnumProperty(
        items=[
            
            ('CONNECT', 'Connected', 'Adam connected'),
            ('DISCONNECT', 'Disconnected', 'Adam disconnected'),
            ('REC', 'Rec', 'Rec animation'),
            ('PAUSE', 'Pause', 'Pause animation'),
            ('SNAP_FACE', 'Stop', 'Stop animation')
            
        ]
    )

    def execute(self, context):
        
        global status
        status = self.action

        if self.action == 'CONNECT':
           self.add_connection(context=context)

        elif self.action == 'DISCONNECT':
             self.add_disconnection(context=context)
             
        elif self.action == 'PAUSE':
             self.StartRecFun(context=context)
             
        elif self.action == 'SNAP_FACE':
             self.StartSaveStop(context=context)
     
        return {'FINISHED'}
        
    @staticmethod
    def add_connection(context):
        client.connect()

    @staticmethod
    def add_disconnection(context):
        client.close()
        
    @staticmethod
    def StartRecFun(context):
        SaveJsonCmd()
        
    @staticmethod
    def StartSaveStop(context):
        SaveAndClearJsonCmd()


class SerializableCommands:
    motors: List[MotorCommand]

    def __init__(self, motors: List[MotorCommand]) -> None:
        self.motors = motors
        
# Generate a list of SerializableCommands objects
serializable_commands_list = []   
        
class Client:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, server_address):
        if not hasattr(self, 'server_address'):
            self.server_address = server_address
            self.client_wssocket = websocket.WebSocket()
            
                        
    def connect(self):
        try:
            self.client_wssocket.connect(self.server_address, ping_interval=0, ping_timeout=None)
            print("connected")
        except: print('Server not answer')
           
            
    def send_json(self, json_data):
        #data = json.dumps(json_data).encode('utf-8')
        data = json_data.encode('utf-8')
        
        self.client_wssocket.send(data)

    def receive(self):
        response = self.client_wssocket.recv(4096)
        return response.decode('utf-8')

    def close(self):
        self.client_wssocket.close()
        print("disconnected")

def jsonCommandList(Head, Right_Hand, Arm_Right, Left_Hand, Arm_Left, 
                    Press_Chest, Leg_Right, Leg_Left):
    
    command_list = [MotorCommand("head", Head[0]),    
                    MotorCommand("neck", Head[1]),
                    MotorCommand("right_hand", Right_Hand),
                    MotorCommand("right_lower_arm_up", Arm_Right[1]),
                    MotorCommand("right_upper_arm", Arm_Right[2]),
                    MotorCommand("right_shoulder", Arm_Right[3]),
                    MotorCommand("left_hand", Left_Hand),
                    MotorCommand("left_lower_arm_up", Arm_Left[1]),
                    MotorCommand("left_upper_arm", Arm_Left[2]),
                    MotorCommand("left_shoulder", Arm_Left[3]),
                    MotorCommand("chest", Press_Chest[2]),
                    MotorCommand("press", Press_Chest[1]),
                    MotorCommand("right_upper_leg", Leg_Right[2]),
                    MotorCommand("right_lower_leg", Leg_Right[1]),
                    MotorCommand("right_foot", Leg_Right[0]),
                    MotorCommand("left_upper_leg", Leg_Left[2]),
                    MotorCommand("left_lower_leg", Leg_Left[1]),
                    MotorCommand("left_foot", Leg_Left[0])]
                    
    serializable_commands = SerializableCommands(command_list)

    # Convert the object to a JSON string
    #serializable_commands_json = json.dumps(serializable_commands.__dict__, default=lambda x: x.__dict__)

    return(serializable_commands)  
            
def calcangles(BonesName, orientation):
    
    bone = bpy.context.scene.objects['Armature']
    arrayElement = []
    ArrayEuler = []        
    for i in range(0, len(BonesName)-1):
        
        j = i + 1 
        try:
            pb1 = bone.pose.bones.get(BonesName[i])
            pb2 = bone.pose.bones.get(BonesName[j])
        
            v1 = pb1.head - pb1.tail
            v2 = pb2.head - pb2.tail
        
            angls = degrees(v1.angle(v2))
            #angls = abs((v1.angle(v2)) * 360 / math.pi)  
                               
        except: print("List index out of range")
        
        arrayElement.append(angls)
        
    i = len(BonesName)-1
    pb = bone.pose.bones[BonesName[i]]
    
    v = pb.matrix_channel.to_euler()
    
    anglx = degrees(v[orientation])
    arrayElement.append(anglx) 
        
           
    #degrees(bpy.context.scene.objects['Armature'].pose.bones['shoulder.l'].matrix_channel.to_euler().x)     
    
    return(arrayElement)

def getBoneLimits(BonesName):
    #bpy.context.scene.objects['Armature'].pose.bones['shoulder.r'].lock_ik_y
    axisLimits = []
    
    bone = bpy.context.scene.objects['Armature']
        
    for i in range(0, len(BonesName)):
        
        try:
            pb1 = bone.pose.bones.get(BonesName[i])
            
            if pb1.lock_ik_x == False:
               axisLimitmin_x = degrees(pb1.ik_min_x)
               axisLimitmax_x = degrees(pb1.ik_max_x)
               
               axisLimitdelta_x = abs(axisLimitmax_x - axisLimitmin_x)
                       
               axisLimits.append(axisLimitdelta_x)
               
               
            if pb1.lock_ik_y == False:
               axisLimitmin_y = degrees(pb1.ik_min_y) #* 360 / math.pi
               axisLimitmax_y = degrees(pb1.ik_max_y) #* 360 / math.pi
                              
               axisLimitdelta_y = abs(axisLimitmax_y - axisLimitmin_y)
                       
               axisLimits.append(axisLimitdelta_y)
               
            if pb1.lock_ik_z == False:
               axisLimitmin_z = degrees(pb1.ik_min_z) #* 360 / math.pi
               axisLimitmax_z = degrees(pb1.ik_max_z) #* 360 / math.pi
 
               axisLimitdelta_z = abs(axisLimitmax_z - axisLimitmin_z)
                       
               axisLimits.append(axisLimitdelta_z)
               
        except: print("List index out of range")
            
    return(axisLimits)
  
def anglToPercent(angles, limits):
        
    AnglPercent = np.divide((angles), (limits))
    AnglPercent = np.multiply(AnglPercent, 100)
    AnglPercent = AnglPercent
    AnglPercent = np.around(AnglPercent, decimals = 1)
    
    return(AnglPercent)
                 
def update(self, scene):

    offsetPercent = 50.0  

    #Calc Head:
    limits = getBoneLimits(Head)
    angles = calcangles(Head, 2) # orientation = (0 - 'x', 1 - 'y', 2 - 'z')
    angles = np.array(angles) - np.array(HeadStartPos)
    angles = np.around(angles, decimals = 1)
    HeadPercent = abs(anglToPercent(angles, limits) - offsetPercent)
        
    #Calc Arm_Right:
    limits = getBoneLimits(Arm_Right)
    angles = calcangles(Arm_Right, 0) # orientation = (0 - 'x', 1 - 'y', 2 - 'z')
    angles = np.array(angles) - np.array(ArmRightStartPos)
    angles = np.around(angles, decimals = 1)
    ArmRightPercent = abs(anglToPercent(angles, limits))

    #Calc Arm_Left:
    limits = getBoneLimits(Arm_Left)
    angles = calcangles(Arm_Left, 0) # orientation = (0 - 'x', 1 - 'y', 2 - 'z')
    angles = np.array(angles) - np.array(ArmLeftStartPos)
    angles = np.around(angles, decimals = 1)
    ArmLeftPercent = abs(anglToPercent(angles, limits))
                
    #Calc Press_Chest:
    limits = getBoneLimits(Press_Chest)
    angles = calcangles(Press_Chest, 2) # orientation = (0 - 'x', 1 - 'y', 2 - 'z')
    angles = np.array(angles) - np.array(PressStartPos)
    angles = np.around(angles, decimals = 1)
    AnglPercent = anglToPercent(angles, limits)
    PressChestPercent = [AnglPercent[0], AnglPercent[1], AnglPercent[3] + offsetPercent]
           
    #Calc Leg_Right:
    limits = getBoneLimits(Leg_Right)
    angles = calcangles(Leg_Right, 0) # orientation = (0 - 'x', 1 - 'y', 2 - 'z')
    angles = np.array(angles) - np.array(LegRightStartPos)
    angles = np.around(angles, decimals = 1)
    LegRightPercent = abs(anglToPercent(angles, limits))
        
    #Calc Leg_Left:
    limits = getBoneLimits(Leg_Left)
    angles = calcangles(Leg_Left, 0) # orientation = (0 - 'x', 1 - 'y', 2 - 'z')
    angles = np.array(angles) - np.array(LegLeftStartPos)
    angles = np.around(angles, decimals = 1)
    LegLeftPercent = abs(anglToPercent(angles, limits))
    
    RightHandPercent = HeadPercent[0]
    LeftHandPercent = HeadPercent[0]
        
    serializable_commands = jsonCommandList(HeadPercent, RightHandPercent, ArmRightPercent, 
                                LeftHandPercent, ArmLeftPercent, PressChestPercent, 
                                LegRightPercent, LegLeftPercent)

    if   status == 'CONNECT':
       # Convert the object to a JSON string
         serializable_commands_json = json.dumps(serializable_commands.__dict__, default=lambda x: x.__dict__)
         SendJsonData(serializable_commands_json)
                       
    elif status == 'REC':
         WriteJsonCmd(serializable_commands)

     

def WriteJsonCmd(json_data):
    serializable_commands_list.append(json_data) 

def SaveJsonCmd():
    with open('json_data.json', mode='w') as outfile:
        
         # Convert the serializable_commands_list to JSON using a lambda function
         serialized_json = json.dumps(serializable_commands_list, default=lambda o: o.__dict__, indent=4)
         outfile.write(serialized_json)
         
def SaveAndClearJsonCmd():
    with open('json_data.json', mode='w') as outfile:
        
         # Convert the serializable_commands_list to JSON using a lambda function
         serialized_json = json.dumps(serializable_commands_list, default=lambda o: o.__dict__, indent=4)
         outfile.write(serialized_json)
         serializable_commands_list.clear()                         

def ClearJsonFile():
    with open('json_data.json', 'w') as outfile:
              outfile.write("")
              serializable_commands_list.clear()
              
def SendJsonData(serializable_commands):
    try:
        client.send_json(serializable_commands)
    except: 
        print("Not connected to server")
    
def unregister():
    bpy.utils.unregister_class(SimpleBoneAnglesPanel)
            
def register():
    
    #clearjsoncomm()
    #bpy.utils.register_class(SimpleBoneAnglesPanel)
    register_class(Conection_PT_Panel)
    register_class(Status_OT_Panel)
    bpy.app.handlers.frame_change_pre.append(update)

    
if __name__ == "__main__":
   
   #client = Client(("ws://localhost:8000")) #old
   #client = Client(("ws://192.168.1.7:8000/adam-2.6/off-board")) #new 
   #client = Client(("ws://192.168.50.10:8002/adam-2.7/off-board")) #new adam 2.7 10.254.254.120
 
   client = Client(("ws://10.254.254.120:8000/adam-2.7/off-board"))
   
   register()

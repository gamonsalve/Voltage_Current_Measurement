import serial #Import python serial library
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
# You can generate an API token from the "API Tokens Tab" in the UI
token = "_3UiGvqpb8fS3gsX1eAebnKgoe5-ERvEdbQFVUeXGEksM2D4RVYsFtuDvEvLSNvETjIEZ7ICPhkLLkdjHWi6iA=="
org = "UQTR"
bucket = "Battery_Data"

influxClient= InfluxDBClient(url="http://localhost:8086", token=token, org=org)
write_api = influxClient.write_api(write_options=SYNCHRONOUS)


#serialPort = serial.Serial("COM3",9600,timeout=1,parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS) #open Serial Port
serialPort = serial.Serial("COM7",9600,timeout=1,parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS) #Ubuntu open Serial Port
i=0
print(datetime.utcnow())
Continue=True;
while Continue:
    try:
        #Read a single ine from serial (Message that ends by LF \n)
        data=serialPort.readline()
        dataString = data.replace(b'\x00', b'').decode('ascii') #Delete null characters
        if data==0x00:
            print("No Data")
        else:
            #Process and Transform data from MCU
            timestamp=datetime.utcnow()
            i=i+1
            dataList=dataString.split(",")
            currentInfo=dataList[0].split("=")
            voltageInfo=dataList[1].split("=")
            if(currentInfo[0]=="Current"):
                currentValue=float(currentInfo[1])
            if(voltageInfo[0]== "Voltage"):
                voltageValue=float(voltageInfo[1])
            #Save Time Series to Influxdb
            point = Point("PowerMeasurement")\
            .field("current", currentValue)\
            .field("voltage",voltageValue)\
            .time(timestamp,write_precision='ns')
            print(datetime.utcnow())
            write_api.write(bucket, org, point)
    except KeyboardInterrupt:
        print("Stop requested by User")
        Continue=False
    except: 
        print("An Error has occurred... Sending Previous Data")
        point = Point("PowerMeasurement")\
        .field("current", currentValue)\
        .field("voltage",voltageValue)\
        .time(timestamp,write_precision='ns')
        print(datetime.utcnow())
        write_api.write(bucket, org, point)
            
            
print(datetime.utcnow())     
serialPort.close()
print("Port Closed")
influxClient.close()
print("client Close")


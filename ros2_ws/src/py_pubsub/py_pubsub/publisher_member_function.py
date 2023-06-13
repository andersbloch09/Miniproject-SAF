import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import xml.etree.ElementTree as ET
import csv
import time
import socket

class XMLPublisherNode(Node):

    def __init__(self):
        super().__init__('xml_publisher_node')
        self.publisher_ = self.create_publisher(String, 'xml_data', 10)
        timer_period = 2.0  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.result = String()

    def timer_callback(self):
        result = self.result
        self.publisher_.publish(result)

def search_csv(id_value):
    csv_file_path = '/home/anders/ros2_ws/src/py_pubsub/py_pubsub/procssing_times_table (1).csv'
    column_name = 'Station#06'
    row_keyword = 'Carrier#'+str(id_value)
    with open(csv_file_path, 'r') as file:
        csv_reader = csv.reader(file, delimiter=';')
        headers = next(csv_reader)  # Read the header row
        try:
            col_index = headers.index(column_name)
            matching_rows = []
            for row in csv_reader:
                if row_keyword in row:
                    matching_rows.append(row[col_index])
            return matching_rows
        except ValueError:
            return None

def parse_xml_data():
        xml_file_path = '/home/anders/ros2_ws/src/py_pubsub/py_pubsub/time.xml'
        # Parse an XML file
        tree = ET.parse(xml_file_path)
        # Parse the XML data and return as a string
        root = tree.getroot()
        id_value = root.find('ID')
        if id_value is not None:
            id_value = id_value.text
            print("ID value:", id_value)
            return id_value
        else:
            print("ID element not found")

def main(args=None):
    rclpy.init(args=args)
    xml_publisher_node = XMLPublisherNode()

    HOST = "172.20.66.41"
    PORT = 11111
    ## Create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ## Bind the socket to a specific address and port
    s.bind((HOST, PORT))
    ## Listen for incoming connections
    s.listen(1)
    ## Wait for a client to connect
    print("Waiting for client")
    conn, addr = s.accept()
    print("Client connected")
    
    while 1:
        #Receive data from the client
        data = conn.recv(1024)
        xml_string_recv = int.from_bytes(data, byteorder="little")
        xml_string_recv = str(xml_string_recv)
        #xml_string = '<?xml version="1.0" encoding="uft-8"?><info><ID>'+'7'+'</ID></info>'
    
        file_path = "/home/anders/ros2_ws/src/py_pubsub/py_pubsub/time.xml"

        root = ET.fromstring(xml_string_recv)
        tree = ET.ElementTree(root)
        tree.write(file_path, encoding='utf-8', xml_declaration=True)
    
        id_value = parse_xml_data()
        process_time = search_csv(id_value)
        
        if process_time == None: 
            print("error")
        else: 
            print(process_time[0])

            process_time_measured = process_time[0]

            xml_publisher_node.result.data = id_value

            #Sends the time back to the PLC
            conn.send(process_time_measured.encode())
            
        rclpy.spin_once(xml_publisher_node)
    xml_publisher_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()


    


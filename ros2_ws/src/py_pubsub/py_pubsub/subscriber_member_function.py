import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import xml.etree.ElementTree as ET
import csv
import socket
import time


class XMLPublisherNode(Node):

    def __init__(self):
        super().__init__('xml_publisher_node')
        self.publisher_ = self.create_publisher(String, 'xml_data', 10)
        timer_period = 2.0  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.xml_file_path = '/home/ulf/Desktop/time.xml'
        self.csv_file_path = '/home/ulf/Desktop/processing_times_table.csv'
        self.station_name = "Station#06"
        self.result = 0

    def timer_callback(self):
        try:
            tree = ET.parse(self.xml_file_path)
            root = tree.getroot()
            # Parse the XML data here and publish the results as a ROS2 message
            id_value = self.parse_xml_data(root)
            msg = String()
            self.publisher_.publish(msg)

            # Search for the ID in the CSV file
            results = self.search_csv(self.csv_file_path, self.station_name, id_value)
            if results is not None:
                self.get_logger().info('CSV Row Data:')
                for result in results:
                    self.get_logger().info(result)
                    self.result = result
            else:
                self.get_logger().info('ID not found in the CSV file.')

        except Exception as e:
            self.get_logger().error('Failed to parse XML file: ' + self.xml_file_path)
            self.get_logger().error(str(e))

    def parse_xml_data(self, root):
        # Parse the XML data and return as a string
        id_element = root.find('ID')
        if id_element is not None:
            id_value = id_element.text
            self.get_logger().info('ID: %s' % id_value)
        else:
            self.get_logger().info('ID element not found in the XML string.')

        return id_value

    def search_csv(self, csv_file, column_name, row_keyword):
        with open(csv_file, 'r') as file:
            csv_reader = csv.reader(file)
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

def main(args=None):
    rclpy.init(args=args)
    xml_publisher_node = XMLPublisherNode()

    HOST = "172.20.66.41"
    PORT = 11111
    first_timer=time.time()
    # Create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to a specific address and port
    s.bind((HOST, PORT))
    # Listen for incoming connections
    s.listen(1)
    # Wait for a client to connect
    print("Waiting for client")
    conn, addr = s.accept()
    print("Client connected")
        
    while 1:

        # Receive data from the client
        data = conn.recv(1024)

        bytes = int.from_bytes(data, byteorder="little")

        process_time = xml_publisher_node.result
        
        #Sends the time back to the PLC
        conn.send(process_time.encode())

        # Process the data
        print(str(bytes))
        xml_string = str(bytes)
        file_path = "/home/ulf/Desktop/time.xml"
        with open(file_path, "w") as file:
            file.write(xml_string)
        rclpy.spin_once(xml_publisher_node)

    
    
    xml_publisher_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()


    


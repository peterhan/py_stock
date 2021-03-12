def check_socket(ip,port):
    import socket
    a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    location = (ip,port)
    result_of_check = a_socket.connect_ex(location)
    return result_of_check==0:


if result_of_check == 0:

   print("Port is open")

else:

   print("Port is not open")
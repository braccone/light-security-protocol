import socket
# import base64
# from Cryptodome.Util.Padding import pad, unpad
# from Cryptodome.Cipher import AES
from Protocol.Encryption import Encryption
from Protocol.AesKey import AesKey
from Protocol.Signature import Signature
import random

# Mqtt message Hello World! 21 bytes https://iot.stackexchange.com/questions/4201/whats-the-size-in-bytes-of-a-single-tls-encrypted-mqtt-message

# Variables For device
KEYDEVICE = bytes.fromhex('2B7E151628AED2A6ABF7158809CF4F3C') 
IVDEVICE = bytes.fromhex('00000000000000000000000000000000')

device = Encryption(KEYDEVICE,IVDEVICE)

# Variables for client
KEYCLIENT = bytes.fromhex('2B7E151628AED2A6ABF7158809CF4F3C')
IVCLIENT = bytes.fromhex('00000000000000000000000000000000')
client = Encryption(KEYCLIENT,IVCLIENT)

# SERVER UDP VARIABLES
localIP = "127.0.0.1"

localPort = 20001

bufferSize = 1024


msgFromServer = "Hello UDP Client"

bytesToSend = str.encode(msgFromServer)


# Create a datagram socket

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)


# Bind to address and ip

UDPServerSocket.bind((localIP, localPort))

# keyTest = AesKey(16).key
# print(f"generate key: {len(keyTest)}")
print("UDP server up and listening")


# Listen for incoming datagrams

while(True):
    try:

        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        print(bytesAddressPair)

        clientMsg = bytesAddressPair[0]

        clientIP = bytesAddressPair[1]

        print(f"Message from Client: {clientMsg}")
        print(f"Client IP Address: {clientIP}")

        if clientMsg[0].__eq__('1'):
            print("-------------FIRST MESSAGE----------------------------")
            # decrypt the MSG 3 Ek,c[OP,PosC, M1, N2]
            msg = clientMsg[1:]
            print(f"Received Message from client({clientIP}): {msg}")
            msgClient1 = client.decrypt(msg)
            msgClient1 = msgClient1.decode("utf-8").split(",")
            operation = msgClient1[0]
            clientPos = msgClient1[1]
            M1 = msgClient1[2]
            N2 = msgClient1[3]
            print(f"msgClient1: {msgClient1}")

            # decrypt with key device M1
            msgDevice1 = device.decrypt(M1)
            msgDevice1 = msgDevice1.decode("utf-8").split(",")
            clientID = msgDevice1[0]
            deviceID = msgDevice1[1]
            N1 = msgDevice1[2]
            print(f"msgDevice1 : {msgDevice1}")
            # device.decrypt("")

            # check if client is allowed to perform operation

            # build OTP msg Ek,d[IDc, OP, N1, N3]
            N3 = str(random.randint(0,10000))
            OTP = "2" + N1 + "," + clientID + "," + N3 + "," + operation
            OTP = bytes(OTP, "utf-8")
            print(f"OTP= {OTP}")
            encryptedOTP = device.encrypt(OTP)
            print(f"Encrypted OTP: {encryptedOTP}")
            N2 = bytes(N2, 'utf-8')
            M4 = client.encrypt(N2 + b"," + encryptedOTP)
            print(f"Message 4 to client: {M4}")

            # save OTP signature in block chain
            signatureOTP = Signature().sign(encryptedOTP)

            # send to client Ek,c [OTP, N2]
            UDPServerSocket.sendto(M4, clientIP)
            print(f"Message 4 sent")

        if clientMsg[0].__eq__('2'):
            print("-------------SECOND MESSAGE----------------------------")
            # decrypt M2 = Ek,d[IDd, OP, Res, N3]
            print(f"Message 2 received: {clientMsg} ")
            msg = clientMsg[1:]
            msg = msg.split(",")
            Res = msg[0]
            M2 = msg[1]
            decryptedM2 = device.decrypt(M2)
            decryptedM2 = decryptedM2.decode("utf-8").split(",")
            IDd = decryptedM2[0]
            OP = decryptedM2[1]
            ResM2 = decryptedM2[2]
            nonce3M2 = decryptedM2[3]

            # check NONCE N3
            if (nonce3M2 != N3):
                pass

            # check if M2 contains the same RES
            if(Res != ResM2):
                pass

            signedM2 = Signature().sign(M2)
            # Save M2 signature in the blockchain

            UDPServerSocket.sendto(b"ok", clientIP)
    except Exception as e:
        print(f"Server Error: {e}")
        pass


    print(clientMsg)
    print(clientIP)

    # Sending a reply to client

    # UDPServerSocket.sendto(bytesToSend, clientIP)

# socket_echo_client_dgram.py
import socket
import sys
import base64
import random
from Cryptodome.Util.Padding import pad, unpad
from Cryptodome.Cipher import AES

# key: 1234123456789878 -- 0x31, 0x32, 0x33, 0x34, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x38, 0x37, 0x38
# iv:  1234567898765432 -- 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x38, 0x37, 0x36, 0x35, 0x34, 0x33, 0x32
# SHOULD BE THE SAME AS THE DEVICE
clientKey = bytes.fromhex('2B7E151628AED2A6ABF7158809CF4F3C')
clientIV = bytes.fromhex('00000000000000000000000000000000')


################## ENCRYPT #####################
# follow the same method of encryption in arduino
# return bytes
def encrypt(msg):
    # create the combination of key and iv for encryption
    cipher = AES.new(clientKey, AES.MODE_CBC, iv=clientIV)
    # encode plaintext in base 64
    msg64 = base64.b64encode(msg)
    # encrypt the msg with padding pkcs7 as arduino
    ciphertext = cipher.encrypt(pad(msg64, AES.block_size, style='pkcs7'))
    # encode the chipertext in base 64
    return base64.b64encode(ciphertext)
################## DECRYPT #####################
# follow the same metho of decryption in arduino
# return bytes


def decrypt(msg):
    cipher = AES.new(clientKey, AES.MODE_CBC, iv=clientIV)
    try:
        # decode from base64
        msg64 = base64.b64decode(msg)
        # Decrypt msg with unpadding
        pt = unpad(cipher.decrypt(msg64), AES.block_size, style='pkcs7')
        return base64.b64decode(pt)
    except ValueError as err:
        print("Decrypt error: {0}".format(err))


# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)

BUFFERSIZE = 1024

# indirizzo della scheda arduino
DEVICE_PORT = 8888
DEVICE_IPADDR = '192.168.1.102'

device_address = (DEVICE_IPADDR, DEVICE_PORT)

# indirizzo del server
SERVER_PORT = 20001
SERVER_IPADDR = "127.0.0.1"

server_address = (SERVER_IPADDR, SERVER_PORT)

message = b'1testclientid'
testSplit = b'2test-idadoada-2131'

try:
    # Send data
    print('sending {!r}'.format(message))
    sent = sock.sendto(message, device_address)
    # while(sent == False):
    #     print("Retrying to send msg to device")
    #     sent = sock.sendto(message, device_address)

    # Receive response
    print('waiting to receive from device')
    data, server = sock.recvfrom(BUFFERSIZE)
    print(f"received from server: {server}")
    if (server[0].__eq__(DEVICE_IPADDR)):
        # generate nonce N2
        N2 = str(random.randint(0,10000))
        N2 = bytes(N2, 'utf-8')
        print(f"porca puttana :{N2}")
        print('received {!r}'.format(data))
        messageToServer1 = b"LOCK" + b"," + b"PosC" + b"," + data + b"," +N2
        encryptedMTS1 = b"1" + encrypt(messageToServer1)
        sentToServer = sock.sendto(encryptedMTS1, server_address)
        print(f"Message 1 to server: {encryptedMTS1}")

        # receive response from server Ekc,s[OTP, N2]
        data, server = sock.recvfrom(BUFFERSIZE)
        if(server[0].__eq__(SERVER_IPADDR)):
            # decrypt with client key
            messageFromServer1 = decrypt(data)
            messageFromServer1 = messageFromServer1.decode("utf-8").split(",")
            print(f"messageFromServer1: {messageFromServer1}")
            nonce2 = messageFromServer1[0]
            OTP = bytes(messageFromServer1[1], "utf-8")
            # check the nonce N2
            if (nonce2 == N2):
                print("N2 error")
                pass
            print(f"Message 2 to device: {OTP}")
            print(f"lunghezza: {len(OTP)}")
            sentToDevice = sock.sendto(OTP, device_address)
             # receive response from server Ekc,s[OTP, N2]
            data, server = sock.recvfrom(BUFFERSIZE)
            print(f"Last Message from device: {data}")
            if(server[0].__eq__(device_address)):
                # decrypt with client key
                messageFromDevice2 = data.decode("utf-8").split(",")
                RES = messageFromDevice2[1]
                M2 = messageFromDevice2[0]
                sentToDevice = sock.sendto(b"2"+data, server_address)

    # print('received {!r}'.format(data))
    # plaintext = decrypt(data)
    # #plaintext = cipher.decrypt(data)
    # print('decrypted msg: ', plaintext.decode("utf-8"))
    # print('sending {!r}'.format(testSplit))
    # sent = sock.sendto(testSplit, server_address)
except Exception as e:
    print(f"Key incorrect or message corrupted: {e}")
finally:
    print('closing socket')
    sock.close()

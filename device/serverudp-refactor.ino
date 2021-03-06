#include <AESLib.h>
#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

long N1 = -1;
long N3 = -1;

byte nonceDevice[N_BLOCK] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
byte nonceServer[N_BLOCK] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
String clientID = "";

// WiFI VARIABLES
const char *ssid = "";
const char *password = "";

WiFiUDP Udp;
unsigned int localUdpPort = 8888; // local port to listen on
char incomingPacket[255];         // buffer for incoming packets
char replyPacket[] = "DAJEE ";    // a reply string to send back

// encryption initialization

AESLib aesLib;

String plaintext = "12345678;";

char cleartext[256];
char ciphertext[512];

// AES Encryption Key
// 2B7E151628AED2A6ABF7158809CF4F3C
// AES Encryption Key
byte aes_key[] = {0x2B, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6, 0xAB, 0xF7, 0x15, 0x88, 0x09, 0xCF, 0x4F, 0x3C};

// General initialization vector (you must use your own IV's in production for full security!!!)
byte aes_iv[N_BLOCK] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

// Sample strings as generated by node.js server
String server_b64iv = "AAAAAAAAAAAAAAAAAAAAAAAA=="; // same as aes_iv  but in Base-64 form as received from server
String server_b64msg = "JS5hY0mtUaNVRYqA1mS7lw==";  // same as aes_iv  but in Base-64 form as received from server

// Generate IV (once)
// void aes_init() {
//   // workaround for incorrect B64 functionality on first run...
//   encrypt( (const char*) "HELLO WORLD!", aes_iv );

//   print_key_iv();

//   // reset aes_iv to server-based value
//   int ivLen = base64_decode((char*)server_b64iv.c_str(), (char *)aes_iv, server_b64iv.length());
// //  Serial.print("Decoded IV bytes: ");
// //  Serial.println(ivLen);
//   print_key_iv();
// }
// Generate IV (once)
void aes_init(byte *nonce, int lenght)
{
  aesLib.gen_iv(aes_iv);
  // workaround for incorrect B64 functionality on first run...
  encrypt("HELLO WORLD!", aes_iv);
}

void resetNonce(byte *nonce)
{
  for (int i = 0; i < sizeof(nonce); i++)
  {
    nonce[i] = 0;
  }
}

String encrypt(char *msg, byte iv[])
{
  int msgLen = strlen(msg);
  char encrypted[2 * msgLen];
  aesLib.encrypt64(msg, msgLen, encrypted, aes_key, sizeof(aes_key), iv);
  return String(encrypted);
}

String decrypt(char *msg, byte iv[])
{
  int msgLen = strlen(msg);
  char decrypted[msgLen]; // half may be enough
  aesLib.decrypt64(msg, msgLen, decrypted, aes_key, sizeof(aes_key), iv);
  return String(decrypted);
}

void sendMessage(char *msg)
{
  Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
  Udp.write(msg);
  Udp.endPacket();
}

void print_key_iv()
{
  Serial.println("AES IV: ");
  for (unsigned int i = 0; i < sizeof(aes_iv); i++)
  {
    Serial.print(aes_iv[i], DEC);
    if ((i + 1) < sizeof(aes_iv))
    {
      Serial.print(",");
    }
  }

  Serial.println("");
}

void clientIdMsg(char *clientID)
{
  Serial.println("CASE IDC");
  // generate nonce
  N1 = random(1000, 10000);
  aesLib.gen_iv(nonceDevice);

  clientID.remove(0, 1);
  Serial.print("clientID: ");
  Serial.println(clientID);
  String msg = clientID + "," + WiFi.macAddress() + "," + nonceDevice;

  Serial.print("M1 :");
  Serial.println(msg);

  String m1 = encrypt((char *)msg.c_str(), enc_iv);
  // sprintf(ciphertext, "%s", encrypted.c_str());
  //Serial.print("Ciphertext: ");
  //Serial.println(m1);
  sendMessage((char *)m1.c_str())
  // Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
  // Udp.write((char*) m1.c_str());
  // Udp.endPacket();
}

bool checkCliendId()
{
  return true;
}

void operationMsg()
{
  // init result
  String res = "";
  // String receviedMsg = incomingPacket;
  char delimiter[] = ",";
  otpMsg.remove(0, 1);
  // initialize first part (string, delimiter)
  // split received msg by ','
  char *ptr = strtok((char *)otpMsg.c_str(), delimiter);
  int cont = 0;
  while (ptr != NULL)
  {
    Serial.printf("found one part: %s -- %ld\n", ptr, N1);
    // check NONCE N1
    if (cont == 0 /* && atol(ptr) != N1 */)
    {
      if (memcmp((char *)nonceDevice, ptr, sizeof(nonceDevice)) != 0)
      {
        // return error 401 REPLAY ATTAK
        Serial.println("wrong nonce");
        res = "error";
        // N1 = -1;
        resetNonce(nonceDevice);
        break;
      }
    }
    // check clientid equals to the one that ask for operation
    if (cont == 1 && strcmp((char *)clientID.c_str(), ptr) != 0)
    {
      // return error 401 different clientid
      Serial.print("wrong client: ");
      Serial.println(clientID);
      resetNonce(nonceDevice);
      res = "error";
      break;
    }
    // set N3
    if (cont == 2)
    {
      N3 = atol(ptr);
      nonceServer = ptr;
    }
    // PERFORM OPERATION
    if (cont == 3)
    {
      //sprintf(operation, "%s", ptr);
      if (strcmp(ptr, "OPEN") == 0)
      {
        Serial.println("LOCKER OPENED!");
        res = "opened";
        sendMessage((char *)res.c_str())
        // Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
        // Udp.write((char *)res.c_str());
        // Udp.endPacket();
        // set delay for locking it
        // return msg
      }

      if (strcmp(ptr, "LOCK") == 0)
      {
        Serial.println("LOCKER LOCKED!");
        res = "locked";
        // return msg
      }
    }

    // create next part
    ptr = strtok(NULL, delimiter);
    cont++;
  }

  // check if idc is the same and N1 is the same
}

void setup()
{
  Serial.begin(115200);
  randomSeed(analogRead(0));

  Serial.println();
  Serial.printf("Connecting to %s ", ssid);
  WiFi.persistent(false);
  WiFi.disconnect(true);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" connected");

  Udp.begin(localUdpPort);
  Serial.printf("Now listening at IP %s, UDP port %d\n", WiFi.localIP().toString().c_str(), localUdpPort);
  Serial.print("MAC: ");
  Serial.println(WiFi.macAddress());

  aes_init();
  aesLib.set_paddingmode(paddingMode::CMS);

  //
  // verify with https://cryptii.com
  // previously: verify with https://gchq.github.io/CyberChef/#recipe=To_Base64('A-Za-z0-9%2B/%3D')
  //

  //   byte enc_iv[N_BLOCK] = { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 }; // iv_block gets written to, provide own fresh copy...
  //  // first decrypt after init should use aes_iv as given by server to test bare string first
  //  String decrypted = decrypt((char*)server_b64msg.c_str(), enc_iv);
  //  Serial.print("Server Cleartext: ");
  //  Serial.println(decrypted);
  //  print_key_iv();
}

void loop()
{
  int packetSize = Udp.parsePacket();
  if (packetSize)
  {
    byte enc_iv[N_BLOCK] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}; // iv_block gets written to, provide own fresh copy...
    // receive incoming UDP packets
    Serial.printf("Received %d bytes from %s, port %d\n", packetSize, Udp.remoteIP().toString().c_str(), Udp.remotePort());
    int len = Udp.read(incomingPacket, packetSize);
    if (len > 3)
    {
      incomingPacket[len] = 0;
    }
    Serial.printf("UDP packet contents: %s\n", incomingPacket);
    // GET IDC AND SEND BACK M1=[IDc,IDc]
    if (incomingPacket[0] == '1')
    {
      clientIdMsg();
    }

    Serial.print("Received OTP msg: ");
    Serial.println(incomingPacket);
    String otpMsg = decrypt((char *)incomingPacket, enc_iv);

    if (otpMsg[0] == '2')
    {
      operationMsg();
    }

    Serial.println("Finished");
  }
}

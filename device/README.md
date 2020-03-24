# Requirements

## Hardware
- ESP8266 ESP-01 ( flash 1 MB - 80 MHz)
- ARDUINO UNO

## Software
- AESLib (https://github.com/suculent/thinx-aes-lib)
- ESP8226 lib: should be set in the preferences of the ide Arduino the following URL-> http://arduino.esp8266.com/stable/package_esp8266com_index.json

# (Important) AES encryption (MODE CBC)
## ENCRYPTION
1. encryption return an hex
2. hex is transformed in base64

## DECRYPTION
1. decode base64
2. the decrypted result is in base64
3. decode base64

# CONNECTING HARDWARE

<img src="images/esp8226-programming.png">

|  *TX* ESP01     |  *PIN11* ARDUINO |
|  *GND* ESP01    |  *GND* ARDUINO   |
|  *CHPD* ESP01   |  *3.3V* ARDUINO  |
|  *GPIO2* ESP01  |                  |
|  *GPIO0* ESP01  |                  |
|  *RST* ESP01	  |                  |
|  *3V3* ESP01    |	 *3.3V* ARDUINO  |
|  *RX* ESP01     |	 *PIN10* ARDUINO |
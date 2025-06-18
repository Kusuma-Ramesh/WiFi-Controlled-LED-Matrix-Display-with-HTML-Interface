#include <WiFi.h>
#include <SPI.h>
#include <MD_Parola.h>
#include <MD_MAX72xx.h>
#include <WiFiClient.h>
#include <WebServer.h>

// Matrix setup
#define HARDWARE_TYPE MD_MAX72XX::FC16_HW
#define MAX_DEVICES 4
#define DATA_PIN 23
#define CS_PIN   5
#define CLK_PIN  18

MD_Parola display = MD_Parola(HARDWARE_TYPE, DATA_PIN, CLK_PIN, CS_PIN, MAX_DEVICES);

// WiFi credentials
const char* ssid = "Horse";
const char* password = "11111111";

WebServer server(80);
String message = "HELLO";

// HTML Page with soft-blinking LED-style circles
const char htmlPage[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>LED Matrix Message Display</title>
  <style>
    @keyframes blink {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.4; }
    }

    body {
      margin: 0;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(to right, #e6f0f3, #f5fafa);
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
    }

    .container {
      background-color: #ffffff;
      padding: 40px 30px;
      border-radius: 12px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
      max-width: 420px;
      width: 90%;
      text-align: center;
    }

    .circle-strip {
      display: flex;
      justify-content: center;
      margin-bottom: 12px;
      gap: 12px;
    }

    .circle {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      animation: blink 1.8s infinite ease-in-out;
    }

    .circle.red {
      background-color: #e74c3c;
      animation-delay: 0s;
    }

    .circle.green {
      background-color: #2ecc71;
      animation-delay: 0.3s;
    }

    .circle.yellow {
      background-color: #f1c40f;
      animation-delay: 0.6s;
    }

    h1 {
      font-size: 22px;
      color: #333;
      margin-bottom: 24px;
    }

    input[type="text"] {
      padding: 12px 10px;
      width: 100%;
      border: 1px solid #ccc;
      border-radius: 6px;
      font-size: 16px;
      margin-bottom: 20px;
      box-sizing: border-box;
      outline: none;
      background-color: #f9f9f9;
      color: #333;
    }

    input[type="text"]:focus {
      border-color: #007BFF;
      box-shadow: 0 0 5px rgba(0, 123, 255, 0.25);
    }

    input[type="submit"] {
      background-color: #007BFF;
      color: white;
      border: none;
      padding: 12px 24px;
      font-size: 16px;
      border-radius: 6px;
      cursor: pointer;
      transition: background-color 0.3s ease;
    }

    input[type="submit"]:hover {
      background-color: #0056b3;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="circle-strip">
      <div class="circle red"></div>
      <div class="circle green"></div>
      <div class="circle yellow"></div>
    </div>
    <h1>LED Matrix Message Display</h1>
    <form action="/" method="GET">
      <input type="text" name="text" placeholder="Enter your message here..." required />
      <br />
      <input type="submit" value="Display on Matrix" />
    </form>
  </div>
</body>
</html>
)rawliteral";

// Handle root path ("/")
void handleRoot() {
  if (server.hasArg("text")) {
    message = server.arg("text");
    display.displayClear();
    display.displayScroll(message.c_str(), PA_CENTER, PA_SCROLL_LEFT, 100);
    Serial.println("Received: " + message);
  }
  server.send(200, "text/html", htmlPage);
}

void setup() {
  Serial.begin(115200);
  delay(2000);
  Serial.println("Booting...");

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 20) {
    delay(500);
    Serial.print(".");
    retries++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi Connected!");
    Serial.print("📡 IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n❌ Failed to connect to WiFi.");
  }

  display.begin();
  display.setIntensity(5);
  display.displayClear();

  server.on("/", handleRoot);
  server.begin();
  Serial.println("🌐 Web server started!");
}

void loop() {
  server.handleClient();
  if (display.displayAnimate()) {
    display.displayReset();
  }
}
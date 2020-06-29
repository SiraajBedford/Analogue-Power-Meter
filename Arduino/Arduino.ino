// Serial communication setup
constexpr long serial_baud_rate = 19200;
constexpr auto serial_config = SERIAL_8E1;

// Frequency modes for TIMER1
#define PWM62k   1   //62500 Hz
#define PWM8k    2   // 7812 Hz
#define PWM1k    3   //  976 Hz
#define PWM244   4   //  244 Hz
#define PWM61    5   //   61 Hz

// Direct PWM change variables
#define PWM9   OCR1A

// Configure the PWM clock The argument is one of the 5 previously defined modes
void pwm91011configure(int mode)
{
  // TCCR1A configuration
  //  00 : Channel A disabled D9
  //  00 : Channel B disabled D10
  //  00 : Channel C disabled D11
  //  01 : Fast PWM 8 bit
  TCCR1A = 1;

  // TCCR1B configuration
  // Clock mode and Fast PWM 8 bit
  TCCR1B = mode | 0x08;

  // TCCR1C configuration
  TCCR1C = 0;
}

// Set PWM to D9
// Argument is PWM between 0 and 255
void pwmSet9(int value)
{
  OCR1A = value; // Set PWM value
  DDRB |= 1 << 5; // Set Output Mode B5
  TCCR1A |= 0x80; // Activate channel
}


/*************** ADDITIONAL DEFINITIONS ******************/

// Macro to converts from duty (0..100) to PWM (0..255)
#define DUTY2PWM(x)  ((255*(x))/100)

/**********************************************************/

// Leonardo board information
constexpr int digital_pins[] = {9, 10, 11};
constexpr int analogue_pins[] = {A0, A1, A2};

const String STUDENT_NUMBER = "21093741";

unsigned long time1 = millis(); // LED receive indicator timer
unsigned long time2 = millis(); // Debug mode timer
unsigned long MillisecondsUpdtime = 0; // Uptime Counter

const byte numChars = 3; // two read bytes + end-of-line
char receivedChars[numChars]; // an array to store the received data

boolean newData = false;
boolean DebugMode = false;

String BinaryString = "";
String Outputstring = "";
int Aread = 0;


void setup() {
  Serial.begin(19200, serial_config);
  pinMode(digital_pins[0], OUTPUT);// the PWM D9 pin
  pinMode(digital_pins[1], OUTPUT);//SR-Latch reset pin ~ S
  pinMode(digital_pins[2], INPUT);// Gonna be the trip status I/P pin
  // Configure Timer 1 (Pins 9, 10 and 11)
  // Valid options are: PWM62k, PWM8k, PWM1k, PWM244 and PWM61
  pwm91011configure(PWM1k);

  // Pins 9 and 6 will change values in the loop function
  // We first configure them
  
  // Prepare pin 9 to use PWM
  // We need to call pwm91011configure before
  pwmSet9(DUTY2PWM(50));
  
}


int value = 0;

void loop()
{

  ReceiveData();
  TransmitData();
  DebugCheck();
  
  PWM9 = value;
  // Increment PWM value and return to 0 after 255
  value=128;

  // LED receive notifier timeout
  if (millis() - time1 > 200) {
    digitalWrite(LED_BUILTIN, LOW);
    time1 = millis();
  }
}

float PhaseFit(float x){
  
  float y = -139.1283 + 9.428192*x - 0.08526877*x*x;//Quadratic Fit
  //float y = 601.5721 - 70.41774*x + 2.465672*x*x - 0.02164616*x*x*x;//Cubic Fit
  //float y = -26482.72 + 4308.243*x - 247.9964*x*x + 5.788783*x*x*x - 0.04257628*x*x*x*x;//Quartic Regression

  return y;
}


float CurrentFit(float x){
  
  //float y = 0.9411445*x + 1.877512;//Linear Fit
  float y = 1.066239 + 0.980841*x - 0.0001196415*x*x;//Quadratic Fit
  return y;
}

//float CurrentFitRMS(float x){
//  
//  float y = 0.9410619*x + 1.343039;//Linear Fit
//  //float y = 0.7726937 + 0.9805599*x - 0.0001683618*x*x;//Quadratic Fit
//  //float y = -0.04139442 + 2.114869*x - 0.05408382*x*x + 0.0002207774*x*x*x;//Cubic Fit
//  return y;
//}




void ReceiveData() {

  char Read_end = '\n';
  static byte rdx = 0;
  char ReadCharacter;


  while (Serial.available() > 0 && newData == false) {

    ReadCharacter = Serial.read();

    digitalWrite(LED_BUILTIN, HIGH);

    if (ReadCharacter != Read_end) {
      receivedChars[rdx] = ReadCharacter;
      rdx++;
      if (rdx >= numChars) {
        rdx = numChars - 1;
      }
    }
    else {
      receivedChars[rdx] = '\0'; // terminate the string
      rdx = 0;
      newData = true;
    }
  }
}

void TransmitData() {
  if (newData == true) {
    if (receivedChars[0] == '0' && DebugMode == false) {
      Serial.println(receivedChars[0]);
      Serial.println(STUDENT_NUMBER);
    }
    if (receivedChars[0] == '1' && DebugMode == false) {
      Serial.println(receivedChars[0]);
      Serial.println(receivedChars[1]);
      //Here you can apply calibration as necessary.
      switch (receivedChars[1]) {
        case '0' : Aread = analogRead(analogue_pins[0]); break;
        case '1' : Aread = analogRead(analogue_pins[1]); break;
        case '2' : Aread = analogRead(analogue_pins[2]); break;
      }


      Serial.println(Aread);
    }
    if (receivedChars[0] == '2' && DebugMode == false) {
      Serial.println(receivedChars[0]);
      Serial.println(receivedChars[1]);
      switch (receivedChars[1]) {
        case '0' : Serial.println(digitalRead(digital_pins[0])); break;
        case '1' : Serial.println(digitalRead(digital_pins[1])); break;
        case '2' : Serial.println(digitalRead(digital_pins[2])); break;
      }
    }
    if (receivedChars[0] == 'x' || receivedChars[0] == 'X') {
      if (receivedChars[1] == '0') {
        DebugMode = false;
      }
      else if (receivedChars[1] == '1') {
        DebugMode = true;
      }
    }

    if ((receivedChars[0] == 'U') && DebugMode == false) // Return uptime if 'U' is received
    {
      MillisecondsUpdtime = millis();
      uptime();
    }

      if ((receivedChars[0] == 'R') && DebugMode == false) // Reset Latch if 'R' is received
    {
      Serial.println(receivedChars[0]);
      Serial.println("Latch has been reset");
      digitalWrite(digital_pins[1], HIGH);
      delay(100);   
      digitalWrite(digital_pins[1], LOW); 
      
    }

  }
  newData = false;
}

void DebugCheck() {
  if (DebugMode == true) {
    String DebugOutput = "";
    int Aread0 = analogRead(analogue_pins[0]);
    delay(10);
    int Aread1 = analogRead(analogue_pins[1]);
    delay(10);
    int Aread2 = analogRead(analogue_pins[2]);
    delay(10);
    DebugOutput = STUDENT_NUMBER + ',' + 
                  "Voltage:" + (float)( ((float)Aread0*5/1024+0.1)*(1600/(100))*(1/(1+1.2))*(1/(1.414)) ) + "(V_AC)"+ ',' + //Voltage_source=(1M/(1M+100k))*(1/(1+1.2/1))
                  "Current:" + (CurrentFit((float)( (( (float)Aread1*5/1024) / ((1+150)*(1+2.2)))*((1/0.03)*1000.0)))*(1/1.414)-5.0)  + "(mA_AC)"+ ',' + //I=(Voltage/(1+R3/R4)*(1+R2/R5))*1/(Rsense), R3=150k, R4=1k, R2=2.2k, R5=1k
                  "Phase:" + abs(PhaseFit((float)( ((float)Aread2*5/1024) /5.0*90.0))) + "(deg)" + ',' +  
                  "TRIP:" + ReturnDigitalRead(digitalRead(digital_pins[2]));

                  
    if (millis() - time2 > 2000) { // LED receive notifier timeout
      Serial.println(DebugOutput);
      time2 = millis();
    }
  }
}

String ReturnDigitalRead(int Input) {
  if (Input == 0) {
    return "LOW";
  }
  else {
    return "HIGH";
  }
}



void uptime()
{
  long days = 0;
  long hours = 0;
  long mins = 0;
  long secs = 0;
  secs = MillisecondsUpdtime / 1000; //convect milliseconds to seconds
  mins = secs / 60; //convert seconds to minutes
  hours = mins / 60; //convert minutes to hours
  days = hours / 24; //convert hours to days
  secs = secs - (mins * 60); //subtract the coverted seconds to minutes in order to display 59 secs max
  mins = mins - (hours * 60); //subtract the coverted minutes to hours in order to display 59 minutes max
  hours = hours - (days * 24); //subtract the coverted hours to days in order to display 23 hours max
  //Display results
  Serial.print("Uptime : ");
  Serial.print(hours);
  Serial.print(":");
  Serial.print(mins);
  Serial.print(":");
  Serial.println(secs);
}


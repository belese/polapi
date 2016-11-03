#include <avr/wdt.h>
#include <avr/interrupt.h>
#include <avr/sleep.h>
#include <TinyWire.h>


#define pwrPin 4
#define btnPin  1
#define killPin 3

#define CMD_GET_VOLTAGE  0x01
#define CMD_GET_BTN_STATE  0x03
#define CMD_GET_FORCE_STOP  0x05


#define WAKE_UP_PRESS 2000 // 2 sec
#define RESET_PRESS 10000 // 120 sec
#define PISTARTTIME 8000
byte own_address = 10;

volatile uint8_t i2c_regs[] =
{
    0xDE, //start byte
    0xAD, //low byte vcc
    0xBE, //high byte vcc
    0xEF, //btn status
};

volatile byte cmd = 0x00;
int cmd_len;

byte data[2];
volatile byte data_position;

byte state;
long start_press;
long started;

int i2c = 0;


void setup() 
{  
  // Read 1.1V reference against AVcc
  // set the reference to Vcc and the measurement to the internal 1.1V reference
  MCUSR &= ~(1<<WDRF); // reset status flag
  wdt_disable();
  ADMUX = _BV(MUX3) | _BV(MUX2);    
  state = 0x02;
  start_press = 0;
  started = millis();
  data_position=0;
  pinMode(pwrPin, OUTPUT);
  digitalWrite(pwrPin, LOW);
  pinMode(btnPin, INPUT_PULLUP);
  pinMode(killPin, INPUT);  
  TinyWire.begin( own_address );  
  TinyWire.onReceive( onI2CReceive );
  TinyWire.onRequest( onI2CRequest );
}

void loop()
{    
  switch (state)
  {
      case 0x00:  //we need to sleep
        sleep();
        break;
      case 0x01:
        check_wake_up(); //check if there is a long press to wake up
        break;
      case 0x02 : //In function        
        //check_initi2c();
        check_reset();
        readVcc();
        readBtnStat();
        readPiStat();
        break;         
  }
}

void reboot() 
{
 // wdt_reset();
 wdt_enable(WDTO_15MS); 
 while (true) {}  
} //reboot

void check_wake_up()
{  
  if (millis() > start_press + WAKE_UP_PRESS)
  {
      //digitalWrite(pwrPin, LOW);
      //state = 0x02; 
      //start_press = 0;
      reboot();
       
  }

  
  if (digitalRead(btnPin))
  {
    state = 0x00;
  }  
}

void stopPower()
{
    digitalWrite(pwrPin, HIGH);
    state = 0x00;    
}

void check_reset()
{
  bool btn = !digitalRead(btnPin); 

  if (!btn)
  {
    start_press = 0;
  }
  else 
  {
    if (start_press == 0)
    {
       start_press = millis();
    }
    else if (millis() > start_press + RESET_PRESS)
    {
       stopPower();    
    }
    
  }     
}


void readPiStat()
{
    //check if pi is on otherwise shutdown
    if (millis() > started + PISTARTTIME)
    {
      if (digitalRead(killPin))
      {
        stopPower();
      }
    }
}

void readBtnStat()
{
    i2c_regs[3] = digitalRead(btnPin);
}

void sleep() 
{    

    GIMSK |= _BV(PCIE);                     // Enable Pin Change Interrupts
    PCMSK |= _BV(PCINT1);                   // Use PB3 as interrupt pin
    ADCSRA &= ~_BV(ADEN);                   // ADC off
    set_sleep_mode(SLEEP_MODE_PWR_DOWN);    // replaces above statement

    sleep_enable();                         // Sets the Sleep Enable bit in the MCUCR Register (SE BIT)
    //sei();                                  // Enable interrupts
    sleep_cpu();                            // sleep

    cli();                                  // Disable interrupts
    PCMSK &= ~_BV(PCINT1);                  // Turn off PB3 as interrupt pin
    sleep_disable();                        // Clear SE bit
    ADCSRA |= _BV(ADEN);                    // ADC on

    sei();                                  // Enable interrupts
    start_press = millis();
    state = 0x01;
    
          
} // sleep




void readVcc() 
{
  ADCSRA |= _BV(ADSC); // Start conversion
  while (bit_is_set(ADCSRA,ADSC)); // measuring
 
  i2c_regs[1] = ADCL; // must read ADCL first - it then locks ADCH  
  i2c_regs[2] = ADCH; // unlocks both   
}

void onI2CReceive(int howMany)
{  
  while(TinyWire.available()>0)
  {
    cmd = TinyWire.read();     
  }   
}

void onI2CRequest() 
{
  if (cmd != 0x00)
  {
    switch (cmd)
    {
      case CMD_GET_VOLTAGE:
        cmd_len = 2;
        data[0]= i2c_regs[1];
        data[1] = i2c_regs[2];
        break;
      case CMD_GET_BTN_STATE:
        cmd_len = 1;
        data[0]= i2c_regs[3];
        break;
      case CMD_GET_FORCE_STOP :    
        stopPower();
        break;
      default:
        cmd_len=0;
    }
    TinyWire.send(0xDE);
    data_position=0;
    cmd = 0x00;    
  }  
  else
  {
    if (data_position < cmd_len)
    {
      TinyWire.send(data[data_position]);
      data_position++;
    }
    else
    {
      TinyWire.send(0xFF);
    }   
  }   
}
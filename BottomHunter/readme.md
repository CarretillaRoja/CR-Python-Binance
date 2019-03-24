## Bottom Hunter

This piece of code allows you to track some coins for the minimum price. It works this way:
- It shows your the amount of BTC available and asks how many you will use.
- Asks for some coins you want to buy. It shows their price and asks at what price you want to start watching them. Eg: 100 satoshis.
- HERE IS THE POINT! You must enter a % to add on top of the coin price. Eg. 3%.

Then, it starts working:
- When the price gets to 100 satoshis, it starts monitoring it, with a buy target at 100 + 3% = 103 satoshis.
- If the price goes down further to 93, it lowers the buy target to 93 + 3% = 96 satoshis.
- Repeat this process if the price keeps going down.
- If the price raises, it lets you know when it gets to 96 satoshis.

As you know, there is a risk (which I am not responsible of!) when the price goes up from the beggining.
If the price goes down the same amount you specified for the %, you are covered and everything will be gains.

This is a PoC, just a simulation, it does not trade with your tokens nor send them anywhere.
If you feel brave, you can add the buy order to the code.

If you feel this code worthy, donations are appreciated:
- ETH: 0x56daD39CCd190D343682a903e0793E7427ECF287
- LTC: MUP3PcZ2QXgJ7CC1cmKTt7jEZDcQPcjcNu

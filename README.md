# HanoverFlipDotClock
Simple clock using a legacy Hanover flip dot bus destination display.
Code is written around the 96x16 (model #M023C) display. 
No attempt is made to work with other models.

The code has a two dimensional array to represent the dots on the display. When required, the code generates 
a message, encoding this array, in the way that the Hanover display expects to see this information. The code
keeps a copy of what it believes is currently on the display... if it is called again to display the same image
(common in a clock) then it doesn't bother to waste the displays time with this communication.


## Acknowledgements
* [hawkz/Hanover_Flipdot ](https://github.com/hawkz/Hanover_Flipdot)I started with this comprehensive project. Probably through my own ignorance
I couldn't make this code work with my display. The author had gone to the trouble of writing the code to accomodate different resolutions but for
me I couldn't get anything to display. I decided to use the understanding of the protocol/checksum from this code but remove any complexity
of supporting different resolutions and focus on getting something working. 

* [tuna-f1sh/node-flipdot](https://github.com/tuna-f1sh/node-flipdot)Background reading, again my ignorance meant I couldn't make the code work.

* [furrtek/HanoverFlipDot](https://github.com/furrtek/HanoverFlipDot)Interesting project where the author has written their own code to handle their display.


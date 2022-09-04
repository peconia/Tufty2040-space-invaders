# Tufty2040-space-invaders
Space invaders style game for the Pimoroni Tufty 2040.

Copy the *space_invaders.py* and *space_invaders_spritesheet.rgb332* onto the Tufty. See [Getting started with Tufty](https://learn.pimoroni.com/article/getting-started-with-tufty-2040) for more information how to.

Start a new game with the up arrow, move left and right with A and C buttons, shoot with B. Careful to not run out of ammo!

![PXL_20220903_174200440_2](https://user-images.githubusercontent.com/7756669/188283183-4b4a185c-41c9-4910-b142-2e752274d381.jpg)


## Running with the main menu

The game file is over 300 lines long, so you may run out of memory if attempting to 
launch the file via the example main menu of the Tufty. To get around this, include the 
*space_invaders<b>.mpy</b>* file instead of the .py one. It has been compiled into bytecode to get 
around the memory limitations.

In order for the main menu to see this file, you need to edit it to check for .mpy files
as well as .py ones. See the example in the *main.py* in this repository, or replace
the main.py on your Tufty with it.

If you make changes of the game and need to compile it to bytecode, you can use
[mpy-cross](https://pypi.org/project/mpy-cross/) to do it.
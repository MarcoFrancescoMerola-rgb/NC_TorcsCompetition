SnakeOil
========
Chris X. Edwards <http://xed.ch>

== Organization
There are two important parts to this entry. 
First is the SnakeOil
module which is a general purpose utility for making SCR entries in
Python. 
If you're interested, you can read about this at:

    http://xed.ch/project/snakeoil

== 
Running The Client
The library parses options and you can execute either `./snakeoil.py -h` or
`./client -h` to see the list of options.


The options are handled like normal Posix options. There are long and
short option forms.


To run an entry start the server and do something like the following.
First the warm-up stage:

    
$ ./client.py --stage 0 --track ovalB --steps 100000 --port 3001 --host localhost
   
 
This will write a file called `ovalB.trackinfo` into the current
directory. This file is then used in the subsequent stages.
The qualifying stage:

    $ ./client.py --stage 1 --track ovalB  --port 3001 --host localhost 

Then to race:

    $ ./client.py --stage 2 --track ovalB  --port 3001 --host localhost 

If the race ends before the specified number of steps (or the 100000
default) then the client will finish counting those at the end, so
just wait a couple of seconds for it to finish.

== Highlights
* I live in San Diego, California, USA. 

* The snakeoil.py library was written to encourage Python programmers
  to enter the SCR. It's quite easy to use to develop your own bot.

* I basically tried to implement all strategies and features.
  I learned that it is better to optimize a simple bot than struggle
  with a sophisticated one.

* My client maps out curves accurately over 180m away. With noise, a
  bit less.

* Mapped a complete turn by turn course description. But it's hard to
  make that be of any use.

* I hesitate to claim to have "optimized". Let's just say that I did
  "improve" the parameters using a genetic algorithm.

* My genetic algorithm has meta parameters that specify how much its
  corresponding parameter can be mutated. This method allows one to
  select not just good parameters but good ranges for mutating them.

* Getting TORCS to be cooperative with high volume testing is probably
  the hardest part of the whole event.

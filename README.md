DSP notes
===

Decode some state and program data from an in-cicuit running ADAU1701 DSP.

Getting started
---
1) attach probes to CS/MOSI/MISO/CLK pins with a Salae logic probe, and capture the boot up and programming
2) Add the SPI decoder and setup the inputs. Then export the traffic to CSV
3) Run `python decode-adad1701.py capture.txt` and review the decoded output

Outputs the last-written value to all control registers, the 5.23 values of the parameter block, and attemps to list the instructions ('steps') that the DSP is running with partial decoding.

The internal architecture of the ADAU1701 seemingly is not reversed yet.

See also
----
* SigmaStudio - the GUI development environment for DSP datapath and filter parameter design
* Arduino library for decoding the XML database output by Sigma studio
* http://www.audiodevelopers.com/4-adau1701-and-sigmastudio/

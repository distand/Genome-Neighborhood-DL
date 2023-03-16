# Genome-Neighborhood-DL
 A little program to scrape genome neighborhood and download genebank file.

## How to use
1. Submit your Job in https://efi.igb.illinois.edu/efi-gnt/ and wait for done.
2. Click button to open GND explorer in a new tab. 
![image](https://user-images.githubusercontent.com/17464561/225482183-60b2359d-f23b-48d2-a5bf-b5199d3cbdd5.png)
3. Copy link.
![image](https://user-images.githubusercontent.com/17464561/225482445-388a78e6-f24c-44a9-b8a7-eafc5fb73169.png)
4. Running main.py, paste link and start.

## Param
- url: full link like https://efi.igb.illinois.edu/efi-gnt/view_diagrams.php?gnn-id=xx&key=xx
- query number[default:1]: the cluster number.
![image](https://user-images.githubusercontent.com/17464561/225482825-a06be2de-8ebb-4c26-a544-b1cc8680757a.png)
- window size[default:10]: genome neighborhood window.
![image](https://user-images.githubusercontent.com/17464561/225483033-66a37fb1-a03d-410a-b53c-801e79eeb050.png)
- download[default:n]: auto download gb file or not.

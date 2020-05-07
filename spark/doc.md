# Setup Spark on SLURM
Download java and spark.tar.gz from the links
```
https://drive.google.com/file/d/1sMgc8sArwJL-tWxgiFOaMpDFwKP7I6Of/view?usp=sharing
https://drive.google.com/file/d/1CljMLDGMuYwA17FK_a1wfvx6oYyQbcw1/view?usp=sharing
```
SCP them to rc login host, extract in the home folder
Add the following lines to `~/.bashrc`
```
SPARK_HOME=$HOME/spark/spark-2.4.5-bin-hadoop2.7
JAVA_HOME=$HOME/java/jdk1.8.0_241
export PATH=$SPARK_HOME/bin:$PATH
export PATH=$JAVA_HOME/bin:$PATH
```
then do `source ~/.bashrc`
### Run spark in interactive session
```
srun --pty -p test -t 30 --mem 8000 /bin/bash slurm_local.cmd
```
### Run spark in multi-node
```
sbatch slurm.cmd
```

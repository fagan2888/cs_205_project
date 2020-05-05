#!/bin/bash
#
#SBATCH -p shared # partition (queue)
#SBATCH -N 6 # number of nodes
#SBATCH -n 10 # number of cores
#SBATCH -t 0-2:00 # time (D-HH:MM)
#SBATCH -o spark-%j.out # STDOUT
#SBATCH -e spark-%j.err # STDERR
#SBATCH --mem=8G

export JAVA_HOME=$HOME/java/jdk1.8.0_241
export SPARK_HOME=$HOME/spark/spark-2.4.5-bin-hadoop2.7/
export MASTER=spark://$HOSTNAME.rc.fas.harvard.edu:7077
export URL=rc.fas.harvard.edu
NODEFILE=nodefile.txt
echo $SLURM_NODELIST | tr -d 'holy7c' | tr -d [ | tr -d ] | perl -pe 's/(\d+)-(\d+)/join(",",$1..$2)/eg' | awk 'BEGIN { RS=","} { print "holy7c"$1}' > $NODEFILE
echo "HOST FILE"
cat $NODEFILE

name=$(echo $SLURM_NODELIST | cut -d '-' -f1 - | tr -d '[')
source "$SPARK_HOME/sbin/start-master.sh"
source "$SPARK_HOME/sbin/start-slave.sh" $MASTER

for cur_node in `cat $NODEFILE`; do
  echo $cur_node
  /usr/bin/ssh $cur_node.$URL "nohup $SPARK_HOME/sbin/start-slave.sh $MASTER" &
done

sleep 30
spark-submit --master $MASTER --deploy-mode client --num-executors 8 P23_spark.py 

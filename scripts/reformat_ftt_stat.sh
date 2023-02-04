rm all_tffs_stat.txt
datadir="../results/smwtp/fft"

Ns='5 6 7 8 9'
RDDS='0.2 0.4 0.6 0.8 1.0'
TFS='0.2 0.4 0.6 0.8 1.0'
SEEDS='0 1 2 3 4'
for n in $Ns
do
	for rdd in $RDDS
	do
        for tf in $TFS
        do
            echo $n $rdd $tf
            for seed in $SEEDS
            do
                awk -f reformat_ftt_stat.awk ${datadir}/"n${n}_rdd${rdd}_tf${tf}_seed${seed}.txt.out" | awk -v N=$n -v RDD=$rdd -v TF=$tf -v S=$seed '{printf("%s %s %s %s ",N,RDD,TF,S); for(i=1;i<=NF;i++) {printf("%s ",$i);} print(""); } ' >> all_tffs_stat.txt
            done
        done
    done
done

cat cnae.txt | while read line; do nohup python3 ComprasCentralizadas.py $line; done

if [ ! -d "./logs" ]; then
    mkdir ./logs
fi

if [ ! -d "./logs/LongForecasting" ]; then
    mkdir ./logs/LongForecasting
fi
seq_len=$[96*20]
model_name=DLinear
label_len=48
pred_len=$[96*10]
modelid=Q1
# for pred_len in 96 192 672
# do
# for seq_len in 1000 2000
# do
# for modelid in P0 P1 P2 P3 P4 P5 P6
# do
python3 -u run_longExp.py \
  --is_training 1 \
  --root_path ./data/CSV/ \
  --data_path $modelid'.csv' \
  --model_id $modelid'_'$seq_len'_'$pred_len \
  --model $model_name \
  --data custom \
  --features S \
  --freq 15min\
  --seq_len $seq_len \
  --label_len $label_len\
  --pred_len $pred_len \
  --target value\
  --enc_in 1 \
  --des 'Exp' \
  --train_epochs 30\
  --do_predict \
  --itr 1 --batch_size 100  --learning_rate 0.005 --individual
# done
# done
# done
# python -u run_longExp.py \
#   --is_training 1 \
#   --root_path ./dataset/ \
#   --data_path traffic.csv \
#   --model_id traffic_$seq_len'_'$pred_len \
#   --model $model_name \
#   --data custom \
#   --features M \
#   --seq_len $seq_len \
#   --pred_len $pred_len \
#   --enc_in 862 \
#   --des 'Exp' \
#   --itr 1 --batch_size 16 --learning_rate 0.005 --individual >logs/LongForecasting/$model_name'_I_'traffic_$seq_len'_'$pred_len.log

# python -u run_longExp.py \
#   --is_training 1 \
#   --root_path ./dataset/ \
#   --data_path weather.csv \
#   --model_id weather_$seq_len'_'$pred_len \
#   --model $model_name \
#   --data custom \
#   --features M \
#   --seq_len $seq_len \
#   --pred_len $pred_len \
#   --enc_in 21 \
#   --des 'Exp' \
#   --itr 1 --batch_size 16 --learning_rate 0.005 --individual >logs/LongForecasting/$model_name'_I_'weather_$seq_len'_'$pred_len.log

# python -u run_longExp.py \
#   --is_training 1 \
#   --root_path ./dataset/ \
#   --data_path exchange_rate.csv \
#   --model_id Exchange_$seq_len'_'$pred_len \
#   --model $model_name \
#   --data custom \
#   --features M \
#   --seq_len $seq_len \
#   --pred_len $pred_len \
#   --enc_in 8 \
#   --des 'Exp' \
#   --itr 1 --batch_size 8 --learning_rate 0.005 --individual >logs/LongForecasting/$model_name'_I_'exchange_$seq_len'_'$pred_len.log

# python -u run_longExp.py \
#   --is_training 1 \
#   --root_path ./dataset/ \
#   --data_path ETTh1.csv \
#   --model_id ETTh1_$seq_len'_'$pred_len \
#   --model $model_name \
#   --data ETTh1 \
#   --features M \
#   --seq_len $seq_len \
#   --pred_len $pred_len \
#   --enc_in 7 \
#   --des 'Exp' \
#   --itr 1 --batch_size 32 --learning_rate 0.005 --individual >logs/LongForecasting/$model_name'_I_'ETTh1_$seq_len'_'$pred_len.log

# # if pred_len=336, lr=0.001; if pred_len=720, lr=0.0001
# python -u run_longExp.py \
#   --is_training 1 \
#   --root_path ./dataset/ \
#   --data_path ETTh2.csv \
#   --model_id ETTh2_$seq_len'_'$pred_len \
#   --model $model_name \
#   --data ETTh2 \
#   --features M \
#   --seq_len $seq_len \
#   --pred_len $pred_len \
#   --enc_in 7 \
#   --des 'Exp' \
#   --itr 1 --batch_size 32 --learning_rate 0.005 --individual >logs/LongForecasting/$model_name'_I_'ETTh2_$seq_len'_'$pred_len.log

# # if pred_len=336, lr=0.005; if pred_len=720, lr=0.0005
# python -u run_longExp.py \
#   --is_training 1 \
#   --root_path ./dataset/ \
#   --data_path ETTm1.csv \
#   --model_id ETTm1_$seq_len'_'$pred_len \
#   --model $model_name \
#   --data ETTm1 \
#   --features M \
#   --seq_len $seq_len \
#   --pred_len $pred_len \
#   --enc_in 7 \
#   --des 'Exp' \
#   --itr 1 --batch_size 8 --learning_rate 0.005 --individual >logs/LongForecasting/$model_name'_I_'ETTm1_$seq_len'_'$pred_len.log

# python -u run_longExp.py \
#   --is_training 1 \
#   --root_path ./dataset/ \
#   --data_path ETTm2.csv \
#   --model_id ETTm2_$seq_len'_'$pred_len \
#   --model $model_name \
#   --data ETTm2 \
#   --features M \
#   --seq_len $seq_len \
#   --pred_len $pred_len \
#   --enc_in 7 \
#   --des 'Exp' \
#   --itr 1 --batch_size 32 --learning_rate 0.01 --individual >logs/LongForecasting/$model_name'_I_'ETTm2_$seq_len'_'$pred_len.log
# done

# seq_len=104
# for pred_len in 24 36 48 60
# do
# python -u run_longExp.py \
#   --is_training 1 \
#   --root_path ./dataset/ \
#   --data_path national_illness.csv \
#   --model_id national_illness_$seq_len'_'$pred_len \
#   --model $model_name \
#   --data custom \
#   --features M \
#   --seq_len $seq_len \
#   --label_len 18 \
#   --pred_len $pred_len \
#   --enc_in 7 \
#   --des 'Exp' \
#   --itr 1 --batch_size 32 --learning_rate 0.01 --individual >logs/LongForecasting/$model_name'_I_'ILI_$seq_len'_'$pred_len.log
# done
#

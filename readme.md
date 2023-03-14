*Restore Stuck Send/Inscribe Ord Wallet Transactions*

This tool allows you to restore stuck transactions by creating a new transaction with the correct fee rate. To use this tool, follow the steps below:

- Determine the adequate fee rate in sat/vB (https://mempool.space/).
- Run the following command in your terminal:

```python3 restore.py <WALLET_NAME> <TXID_OF_STUCK_TX> <FEE_RATE>```

    Replace <WALLET_NAME> with the name of your wallet.
    Replace <TXID_OF_STUCK_TX> with the transaction ID of the stuck transaction.
    Replace <FEE_RATE> with the fee rate in sat/vB.

**How it Works:**

The tool will craft a new transaction using all of the previous inputs and outputs. If your wallet has at least 0.00015 BTC, the tool will add additional inputs to cover the fee and create a new output with 0.00015 BTC to subtract the fee. Any remaining funds will be returned to your wallet. The tool will also set new addresses for the previous outputs and create a change address.

If your wallet has a zero balance, the restore transaction will subtract the fee amount from itself on the last output index.

***It is recommended to have at least 0.00015 BTC in your wallet to cover the restore fee. If you don't have sufficient funds, there is a risk that the rare Satoshi you were sending/inscribing may be consumed by the fee. While I cannot guarantee, in one test without additional funds, the inscription was preserved.***


To increase the amount spare for the fee (min.: 0.00015 btc), run:

```python3 restore.py <WALLET_NAME> <TXID_OF_STUCK_TX> <FEE_RATE> <FEE_AMOUNT>```


Coffee Jar:  bc1ptdxxs3m5m8hzu27qd63ce03ldpurryuh8husqt8x28hwxcr09uns6htug3 




**Restore a stuck send transaction of 1 sat/vB (with funds in wallet - Inscription preserved and back to wallet):**

https://mempool.space/tx/2671bda935de91cf885a8fc78a5dfb8238b8aacdacf279676e7d7c18830bb70b
![image](https://user-images.githubusercontent.com/85583249/224977882-7f2fd0ff-5514-4bf5-b360-30bc8077c9c8.png)


**Restore of a stuck send transaction of 1 sat/vB: (without funds in wallet - Inscription preserved and back to wallet):**

https://mempool.space/tx/9764591bdd04b713ee2fb3e34446cc7001ae2af1e971d5d7ddf6b02e4f2abaf1
![image](https://user-images.githubusercontent.com/85583249/224993925-d9536ae5-bb51-445d-ac7f-5c79380e4c54.png)


**Restore of a stuck inscribe transaction of 1 sat/vB:**

https://mempool.space/tx/7522aa725b2576d8abbe6e7a0e13a81f658909eff290a1f1f564b97938f484b8
![image](https://user-images.githubusercontent.com/85583249/225000726-d097803a-fc84-43cc-a189-701c68f707cc.png)

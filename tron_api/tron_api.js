const TronWeb = require('tronweb');
const HttpProvider = TronWeb.providers.HttpProvider;
const fullNode = new HttpProvider("http://34.237.210.82:8090");

const solidityNode = new HttpProvider("http://34.237.210.82:8091");
const eventServer = new HttpProvider("http://34.237.210.82:8090");
api_key = ""

const CONTRACT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t";

const express = require('express')
const fs = require('fs');
const bodyParser = require('body-parser')
const app = express()

app.use(bodyParser.urlencoded({extended: false}))
app.use(bodyParser.json())

async function transferTRX(amount, toAccount, senderAddress, senderPrivate) {
    const tronWeb = new TronWeb(fullNode, solidityNode, eventServer, senderPrivate);
    tradeobj = await tronWeb.transactionBuilder.sendTrx(
        toAccount,
        amount,
        senderAddress
    );
    const signedtxn = await tronWeb.trx.sign(
        tradeobj,
        senderPrivate
    );
    const receipt = await tronWeb.trx.sendRawTransaction(
        signedtxn
    );
    return receipt
}

async function transferTRC(amount, fromAccount, toAccount, PrivateKey) {
    const tronWeb = new TronWeb(fullNode, solidityNode, eventServer, PrivateKey);
    const {
        abi
    } = await tronWeb.trx.getContract(CONTRACT);

    const contract = tronWeb.contract(abi.entrys, CONTRACT);

    const balance = await contract.methods.balanceOf(fromAccount).call();
    if (balance.toString + 0 < amount + 0) {
        resp = "Недостаточно средств"
        return resp
    }
    resp = await contract.methods.transfer(toAccount, amount).send();
    return resp
}

async function balance(address, privateKey) {
    const tronWeb = new TronWeb(fullNode, solidityNode, eventServer, privateKey)
    const {
        abi
    } = await tronWeb.trx.getContract(CONTRACT);

    const contract = tronWeb.contract(abi.entrys, CONTRACT);

    const balance = await contract.methods.balanceOf(address).call();
    resp = balance.toString()
    return resp
}

async function balanceTRX(address, privateKey) {
    const tronWeb = new TronWeb("https://api.trongrid.io", "https://api.trongrid.io", "https://api.trongrid.io", privateKey)
    let tradeobj = await tronWeb.trx.getAccount(
        address,
    );
    return tradeobj.balance.toString()
}

app.post('/checkBalanceTRC', function (req, res) {
    response = {}
    done = false
    try {
        response = req.body
        ADDRESS = response.address
        privateKey = response.sender_private
        if (req.headers.authorization) {
            if (req.headers.authorization == key.api_key) {
                done = true
            }
        }
    } catch (error) {
        res.send("Bad request_handlerTRC")
    }
    if (done) {
        response_string = ""
        balance(ADDRESS, privateKey).then((resp) => {
            res.send((resp))
        })
            .catch((err) => {
                response_string = "error: " + err
                res.send(response_string)
            });
    } else {
        res.send("not today")
    }
})

app.post('/checkBalanceTRX', function (req, res) {
    response = {}
    done = false
    try {
        response = req.body
        ADDRESS = response.address
        privateKey = response.sender_private
        if (req.headers.authorization) {
            if (req.headers.authorization == key.api_key) {
                done = true
            }
        }
    } catch (error) {
        res.send("Bad request_handlerTRC")
    }
    if (done) {
        response_string = ""
        balanceTRX(ADDRESS, privateKey).then((resp) => {
            res.send((resp))
        })
            .catch((err) => {
                response_string = "error: " + err
                res.send(response_string)
            });
    } else {
        res.send("not today")
    }
})

app.post('/sendTRC', function (req, res) {
    response = {}
    done = false
    try {
        response = req.body
        AMOUNT = response.amount
        fromAccount = response.from_account
        toAccount = response.to_account
        privateKeyTmp = response.private_key
        if (req.headers.authorization) {
            if (req.headers.authorization == key.api_key) {
                done = true
            }
        }
    } catch (error) {
        res.send("Bad request")
    }
    if (done) {
        response_string = ""
        transferTRC(AMOUNT, fromAccount, toAccount, privateKeyTmp).then((resp) => {
            response_string = "ok"
            res.send(resp)
        })
            .catch((err) => {
                response_string = "error: " + err
                res.send(response_string)
                return
            });
    } else {
        res.send("not today")
    }
})

app.post('/sendTRX', function (req, res) {
    response = {}
    done = false
    try {
        response = req.body
        AMOUNT = response.amount
        toAccount = response.to_account
        senderAddress = response.sender_address
        senderPrivate = response.sender_private
        if (req.headers.authorization) {
            if (req.headers.authorization == key.api_key) {
                done = true
            }
        }
    } catch (error) {
        res.send("Bad request" + "\n" + error)
    }
    if (done) {
        response_string = ""
        transferTRX(AMOUNT, toAccount, senderAddress, senderPrivate).then((resp) => {
            response_string = "ok"
            res.send(resp)
        })
            .catch((err) => {
                response_string = "error: " + err
                res.send(response_string)
            });
    } else {
        res.send("not today")
    }
})


app.listen(9707)

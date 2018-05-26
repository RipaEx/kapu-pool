var ripa = require('ripajs');
var request = require('request');
var phassphrases = require('./passphrases');
var constants = require('./constants');
var payments = require('../payments');
var logger = require('winston');
logger.level = 'info';

const ENDPOINT = constants.MAIN_NET_ENDPOINT;//constants.DEV_NET_ENDPOINT;//
const SEND = true;

var callback = function (error, response, body) {
    if (error)
        logger.error(error);
    else
        logger.info(body);
};
var nethashExpected = constants.MAIN_NET_NETHASH;
var passphrase = phassphrases.PASSPHRASE_MAINNET;
var secondPassphrase = phassphrases.SECOND_PASSPHRASE_MAINNET;
if (ENDPOINT === constants.DEV_NET_ENDPOINT) {
    payments = require('./paymentsDevNET');
    ripa.crypto.setNetworkVersion(ripa.networks.devnet.pubKeyHash);
    nethashExpected = constants.DEV_NET_NETHASH;
    passphrase = phassphrases.PASSPHRASE_DEVNET;
    secondPassphrase = phassphrases.SECOND_PASSPHRASE_DEVNET;
    logger.level = 'debug';
}
logger.info('API endpoint: %s', ENDPOINT);
if (payments !== null) {
    logger.debug('Payments array: %s', JSON.stringify(payments));
    var nethash;
    request({
        url: ENDPOINT + constants.GET_NET_HASH_ENDPOINT,
        json: true,
        method: 'GET',
        headers: {
            'Content-Type': constants.HEADER_CONTENT_TYPE,
            'os': constants.HEADER_OS,
            'version': constants.HEADER_VERSION,
            'port': constants.HEADER_PORT,
            'nethash': 'wrong-nethash'
        }
    }, function (error, response, body) {
        nethash = body.nethash;
        logger.debug('NetHash: ' + nethash);
        logger.debug('NetHash Expected: ' + nethashExpected);
        if (nethash === nethashExpected) {
            /*
                Cycle through payments
            */
            var transactionsObject = payments.transactions;
            //logger.debug("Transactions: " + JSON.stringify(transactionsObject));
            var transactionsPendingObject = payments.transactionsPending;
            var donationsObject = payments.donations;
            //logger.debug("Donations: " + JSON.stringify(donationsObject));
            var donationsPercentageObject = payments.donationsPercentage;
            var transactionsRequest = {};
            var transactionsRequestKey = 'transactions';
            transactionsRequest[transactionsRequestKey] = [];
            //Send Transactions Pending
            for (var key in transactionsObject) {
                if (transactionsObject[key].recipientId && transactionsObject[key].amount) {
                    var transaction = ripa.transaction.createTransaction(transactionsObject[key].recipientId, transactionsObject[key].amount, constants.MESSAGE_1, passphrase, secondPassphrase);
                    transactionsRequest[transactionsRequestKey].push(transaction);
                }
            }
            //Send Transactions Pending
            for (var key in transactionsPendingObject) {
                if (transactionsPendingObject[key].recipientId && transactionsPendingObject[key].amount) {
                    var transaction = ripa.transaction.createTransaction(transactionsPendingObject[key].recipientId, transactionsPendingObject[key].amount, constants.MESSAGE_1, passphrase, secondPassphrase);
                    transactionsRequest[transactionsRequestKey].push(transaction);
                }
            }
            //Send Donations
            for (var key in donationsObject) {
                if (donationsObject[key].recipientId && donationsObject[key].amount) {
                    var transaction = ripa.transaction.createTransaction(donationsObject[key].recipientId, donationsObject[key].amount, constants.MESSAGE_2, passphrase, secondPassphrase);
                    transactionsRequest[transactionsRequestKey].push(transaction);
                }
            }
            //Send Donations Percentage
            for (var key in donationsPercentageObject) {
                if (donationsPercentageObject[key].recipientId && donationsPercentageObject[key].amount) {
                    var transaction = ripa.transaction.createTransaction(donationsPercentageObject[key].recipientId, donationsPercentageObject[key].amount, constants.MESSAGE_2, passphrase, secondPassphrase);
                    transactionsRequest[transactionsRequestKey].push(transaction);
                }
            }
            logger.debug(JSON.stringify(transactionsRequest));
            //logger.debug({ transactions: [transaction] });
            /*
                Send transaction
            */
            if (SEND) {
                request({
                    url: ENDPOINT + constants.TRANSACTIONS_ENDPOINT,
                    json: transactionsRequest,
                    //json: { transactions: [transaction] },
                    method: 'POST',
                    headers: {
                        'Content-Type': constants.HEADER_CONTENT_TYPE,
                        'os': constants.HEADER_OS,
                        'version': constants.HEADER_VERSION,
                        'port': constants.HEADER_PORT,
                        'nethash': nethash
                    }
                }, callback);
            } else {
                logger.debug("Transactions not sent");
            }
        } else {
            logger.error("ERROR: nethash is wrong");
        }
    });
} else {
    logger.error("ERROR: payments file is empty");
}
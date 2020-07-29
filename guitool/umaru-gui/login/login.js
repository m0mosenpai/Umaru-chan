const API = require("@chris-kode/myanimelist-api-v2");
const express  = require("express");
const axios = require('axios')

require('dotenv').config();
let app = express();

//res.redirect(urlToRedirect);
const CLIENT_ID = process.env.CLIENT_ID;
const oauth = new API.OAUTH(CLIENT_ID);
const pkceChallenge = require("pkce-challenge");

// Save value of this variable in JSON or Database
const pkce = pkceChallenge();
//console.log(pkce);

const urlToRedirect = oauth.urlAuthorize(pkce.code_challenge);
//console.log(urlToRedirect);

app.get('/oauth', (req, res) => {
    res.redirect(urlToRedirect);
});

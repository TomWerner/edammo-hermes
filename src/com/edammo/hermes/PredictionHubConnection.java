package com.edammo.hermes;

/**
 * Created by Andy on 10/25/2016.
 */

import java.net.*;

public class PredictionHubConnection {
    private final String UPDATE_PRICES_URL = "predictions/update_prices/";
    private final String GET_ORDERS_URL = "";

    private String prediction_hub_ip;
    private String prediction_hub_port;

    public PredictionHubConnection(String prediction_hub_ip, String prediction_hub_port){
        this.prediction_hub_ip = prediction_hub_ip;
        this.prediction_hub_port = prediction_hub_port;
    }

    public void upload_prices(){
    }

    public void get_orders(){
    }
}

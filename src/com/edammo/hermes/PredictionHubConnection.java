package com.edammo.hermes;

/**
 * Created by Andy on 10/25/2016.
 */

import java.net.*;
import java.io.IOException;


public class PredictionHubConnection {
    private static final String GET_CONFIG_URL = "/api/hermes/configuration";
    private static final String UPDATE_PRICES_URL = "/predictions/update_prices/";
    private static final String GET_ORDERS_URL = "/api/hermes/orders";

    private final HttpURLConnection config_conn;
    private final HttpURLConnection prices_conn;
    private final HttpURLConnection orders_conn;

    PredictionHubConnection(String prediction_hub_ip, String prediction_hub_port)
            throws MalformedURLException, IOException {
        try {
            // ping prediction hub here to test server
            URL config_url = new URL("http://" + prediction_hub_ip + ":" + prediction_hub_port + GET_CONFIG_URL);
            URL prices_url = new URL("http://" + prediction_hub_ip + ":" + prediction_hub_port + UPDATE_PRICES_URL);
            URL orders_url = new URL("http://" + prediction_hub_ip + ":" + prediction_hub_port + GET_ORDERS_URL);

            config_conn = (HttpURLConnection) config_url.openConnection();
            prices_conn = (HttpURLConnection) prices_url.openConnection();
            orders_conn = (HttpURLConnection) orders_url.openConnection();
        } catch (MalformedURLException e){
            throw e;
        } catch (IOException e) {
            System.out.println("Unable to connect to the Prediction Hub");
            throw e;
        }
    }
    void connect() throws IOException {
        try{
            config_conn.connect();
            prices_conn.connect();
            orders_conn.connect();
        } catch (IOException e) {
            System.out.println("Unable to connect to the Prediction Hub");
            throw e;
        }
    }

    void get_configuration(){
    }

    void upload_prices(){}

    void upload_account_status(){}

    void get_orders(){}
}

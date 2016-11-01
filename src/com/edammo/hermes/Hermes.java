package com.edammo.hermes;

/**
 * Created by Andy on 10/25/2016.
 */

import com.google.api.client.http.*;
import com.google.api.client.http.javanet.NetHttpTransport;
import com.google.api.client.json.gson.GsonFactory;
import com.google.api.client.json.JsonObjectParser;
import com.google.api.client.util.Key;

import com.ib.controller.NewContract;
import com.ib.controller.NewOrder;
import com.ib.controller.OrderType;
import com.ib.controller.Types;

import java.io.IOException;
import java.util.List;
import java.util.ArrayList;


class Hermes {
    private static final String GET_CONFIG_URL_SUFFIX = "/api/hermes/configuration";
    private static final String GET_ORDERS_URL_SUFFIX = "/api/hermes/order";

    private final GenericUrl config_url;
    private final GenericUrl orders_url;
    private final HttpRequestFactory requestFactory;
    private Configuration config;

    public static class Configuration {
        @Key
        public String account;

        @Key
        public String currency;
    }

    public static class ActionList {
        @Key
        public List<Action> actions;
    }

    public static class Action {
        @Key
        public String symbol;

        @Key
        public int shares;

        @Key
        public String exchange;

        @Key
        public String primaryExchange;

        @Key
        public String orderType;
    }

    private static class HermesContract extends NewContract {
        HermesContract(Action a, Configuration c) {
            this.symbol(a.symbol);
            this.secType(Types.SecType.STK);
            this.exchange(a.exchange);
            this.primaryExch(a.primaryExchange);
            this.currency(c.currency);
        }
    }

    private static class HermesOrder extends NewOrder {
        HermesOrder(Action a, Configuration c) {
            this.account(c.account);
            this.action((a.orderType.equals("buy") ? Types.Action.BUY : Types.Action.SELL));
            this.totalQuantity(a.shares);
            this.orderType(OrderType.MKT);
        }
    }

    public static class HermesContractOrder {
        final NewContract c;
        final NewOrder o;

        HermesContractOrder(Action a, Configuration c) {
            this.c = new HermesContract(a, c);
            this.o = new HermesOrder(a, c);
        }
    }

    Hermes(String prediction_hub_ip, String prediction_hub_port) {
        config_url = new GenericUrl("http://" + prediction_hub_ip + ":" + prediction_hub_port + GET_CONFIG_URL_SUFFIX);
        orders_url = new GenericUrl("http://" + prediction_hub_ip + ":" + prediction_hub_port + GET_ORDERS_URL_SUFFIX);

        requestFactory = new NetHttpTransport().createRequestFactory(new HttpRequestInitializer() {
            @Override
            public void initialize(HttpRequest request) {
                request.setParser(new JsonObjectParser(new GsonFactory()));
            }
        });
    }

    void get_configuration() throws IOException {
        config = requestFactory.buildGetRequest(config_url).execute().parseAs(Configuration.class);
    }

    ArrayList<HermesContractOrder> get_orders() throws IOException {
        ActionList action_list = requestFactory.buildGetRequest(orders_url).execute().parseAs(ActionList.class);
        ArrayList<HermesContractOrder> order_list = new ArrayList<>();
        for (Action a : action_list.actions) {
            order_list.add(new HermesContractOrder(a, config));
        }
        return order_list;
    }
}

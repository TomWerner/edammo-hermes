﻿/* Copyright (C) 2013 Interactive Brokers LLC. All rights reserved.  This code is subject to the terms
 * and conditions of the IB API Non-Commercial License or the IB API Commercial License, as applicable. */
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using IBApi;
using IBSampleApp.messages;
using IBSampleApp.types;

namespace IBSampleApp.ui
{
    public class ContractManager
    {
        private IBClient ibClient;
        private TextBox fundamentals;
        private DataGridView contractDetailsGrid;
        private DataGridView bondContractDetailsGrid;
        private ComboContractResults comboContractResults;

        public const int CONTRACT_ID_BASE = 60000000;
        public const int CONTRACT_DETAILS_ID = CONTRACT_ID_BASE + 1;
        public const int FUNDAMENTALS_ID = CONTRACT_ID_BASE + 2;

        private bool isComboLegRequest = false;

        private bool contractRequestActive = false;
        private bool fundamentalsRequestActive = false;

        public ContractManager(IBClient ibClient, TextBox fundamentalsOutput, DataGridView contractDetailsGrid, DataGridView bondContractDetailsGrid)
        {
            IbClient = ibClient;
            Fundamentals = fundamentalsOutput;
            ContractDetailsGrid = contractDetailsGrid;
            BondContractDetailsGrid = bondContractDetailsGrid;
            comboContractResults = new ComboContractResults();

        }

        public void UpdateUI(ContractDetailsMessage message)
        {

            if (isComboLegRequest)
                comboContractResults.UpdateUI(message);
            else
                HandleContractMessage(message);
        }

        public void HandleContractDataEndMessage(ContractDetailsEndMessage contractDetailsEndMessage)
        {
            if (IsComboLegRequest)
                comboContractResults.Show();

            contractRequestActive = false;
            IsComboLegRequest = false;
        }

        public void HandleBondContractMessage(BondContractDetailsMessage bondContractDetailsMessage)
        {
            BondContractDetailsGrid.Rows.Add(1);

            BondContractDetailsGrid[0, BondContractDetailsGrid.Rows.Count - 1].Value = bondContractDetailsMessage.ContractDetails.Summary.ConId;
            BondContractDetailsGrid[1, BondContractDetailsGrid.Rows.Count - 1].Value = bondContractDetailsMessage.ContractDetails.Summary.Symbol;
            BondContractDetailsGrid[2, BondContractDetailsGrid.Rows.Count - 1].Value = bondContractDetailsMessage.ContractDetails.Summary.Exchange;
            BondContractDetailsGrid[3, BondContractDetailsGrid.Rows.Count - 1].Value = bondContractDetailsMessage.ContractDetails.Summary.Currency;
            BondContractDetailsGrid[4, BondContractDetailsGrid.Rows.Count - 1].Value = bondContractDetailsMessage.ContractDetails.Summary.TradingClass;
            BondContractDetailsGrid[5, BondContractDetailsGrid.Rows.Count - 1].Value = bondContractDetailsMessage.ContractDetails.MarketName;
            BondContractDetailsGrid[6, BondContractDetailsGrid.Rows.Count - 1].Value = bondContractDetailsMessage.ContractDetails.MinTick;
            BondContractDetailsGrid[7, BondContractDetailsGrid.Rows.Count - 1].Value = bondContractDetailsMessage.ContractDetails.OrderTypes;
            BondContractDetailsGrid[8, BondContractDetailsGrid.Rows.Count - 1].Value = bondContractDetailsMessage.ContractDetails.ValidExchanges;
            BondContractDetailsGrid[9, BondContractDetailsGrid.Rows.Count - 1].Value = bondContractDetailsMessage.ContractDetails.LongName;
            BondContractDetailsGrid[10, BondContractDetailsGrid.Rows.Count - 1].Value = bondContractDetailsMessage.ContractDetails.MdSizeMultiplier;
            BondContractDetailsGrid[11, BondContractDetailsGrid.Rows.Count - 1].Value = bondContractDetailsMessage.ContractDetails.AggGroup;
            BondContractDetailsGrid[12, BondContractDetailsGrid.Rows.Count - 1].Value = bondContractDetailsMessage.ContractDetails.Cusip;
            BondContractDetailsGrid[13, BondContractDetailsGrid.Rows.Count - 1].Value = bondContractDetailsMessage.ContractDetails.Ratings;
            BondContractDetailsGrid[14, BondContractDetailsGrid.Rows.Count - 1].Value = bondContractDetailsMessage.ContractDetails.DescAppend;
            BondContractDetailsGrid[15, BondContractDetailsGrid.Rows.Count - 1].Value = bondContractDetailsMessage.ContractDetails.BondType;
            BondContractDetailsGrid[16, BondContractDetailsGrid.Rows.Count - 1].Value = bondContractDetailsMessage.ContractDetails.CouponType;
            BondContractDetailsGrid[17, BondContractDetailsGrid.Rows.Count - 1].Value = bondContractDetailsMessage.ContractDetails.Callable;
            BondContractDetailsGrid[18, BondContractDetailsGrid.Rows.Count - 1].Value = bondContractDetailsMessage.ContractDetails.Putable;
            BondContractDetailsGrid[19, BondContractDetailsGrid.Rows.Count - 1].Value = bondContractDetailsMessage.ContractDetails.Coupon;
            BondContractDetailsGrid[20, BondContractDetailsGrid.Rows.Count - 1].Value = bondContractDetailsMessage.ContractDetails.Convertible;
            BondContractDetailsGrid[21, BondContractDetailsGrid.Rows.Count - 1].Value = bondContractDetailsMessage.ContractDetails.Maturity;
            BondContractDetailsGrid[22, BondContractDetailsGrid.Rows.Count - 1].Value = bondContractDetailsMessage.ContractDetails.IssueDate;
            BondContractDetailsGrid[23, BondContractDetailsGrid.Rows.Count - 1].Value = bondContractDetailsMessage.ContractDetails.NextOptionDate;
            BondContractDetailsGrid[24, BondContractDetailsGrid.Rows.Count - 1].Value = bondContractDetailsMessage.ContractDetails.NextOptionType;
            BondContractDetailsGrid[25, BondContractDetailsGrid.Rows.Count - 1].Value = bondContractDetailsMessage.ContractDetails.NextOptionPartial;
            BondContractDetailsGrid[26, BondContractDetailsGrid.Rows.Count - 1].Value = bondContractDetailsMessage.ContractDetails.Notes;
        }


        public void HandleContractMessage(ContractDetailsMessage contractDetailsMessage)
        {
            ContractDetailsGrid.Rows.Add(1);
            ContractDetailsGrid[0, ContractDetailsGrid.Rows.Count - 1].Value = contractDetailsMessage.ContractDetails.Summary.Symbol;
            ContractDetailsGrid[1, ContractDetailsGrid.Rows.Count - 1].Value = contractDetailsMessage.ContractDetails.Summary.LocalSymbol;
            ContractDetailsGrid[2, ContractDetailsGrid.Rows.Count - 1].Value = contractDetailsMessage.ContractDetails.Summary.SecType;
            ContractDetailsGrid[3, ContractDetailsGrid.Rows.Count - 1].Value = contractDetailsMessage.ContractDetails.Summary.Currency;
            ContractDetailsGrid[4, ContractDetailsGrid.Rows.Count - 1].Value = contractDetailsMessage.ContractDetails.Summary.Exchange;
            ContractDetailsGrid[5, ContractDetailsGrid.Rows.Count - 1].Value = contractDetailsMessage.ContractDetails.Summary.PrimaryExch;
            ContractDetailsGrid[6, ContractDetailsGrid.Rows.Count - 1].Value = contractDetailsMessage.ContractDetails.Summary.LastTradeDateOrContractMonth;
            ContractDetailsGrid[7, ContractDetailsGrid.Rows.Count - 1].Value = contractDetailsMessage.ContractDetails.Summary.Multiplier;
            ContractDetailsGrid[8, ContractDetailsGrid.Rows.Count - 1].Value = contractDetailsMessage.ContractDetails.Summary.Strike;
            ContractDetailsGrid[9, ContractDetailsGrid.Rows.Count - 1].Value = contractDetailsMessage.ContractDetails.Summary.Right;
            ContractDetailsGrid[10, ContractDetailsGrid.Rows.Count - 1].Value = contractDetailsMessage.ContractDetails.Summary.ConId;
            ContractDetailsGrid[11, ContractDetailsGrid.Rows.Count - 1].Value = contractDetailsMessage.ContractDetails.MdSizeMultiplier;
            ContractDetailsGrid[12, ContractDetailsGrid.Rows.Count - 1].Value = contractDetailsMessage.ContractDetails.AggGroup;
        }

        public void HandleRequestError(int requestId)
        {
            if (requestId == CONTRACT_DETAILS_ID)
            {
                isComboLegRequest = false;
                contractRequestActive = false;
            }
            else if (requestId == FUNDAMENTALS_ID)
                fundamentalsRequestActive = false;
        }

        public void HandleFundamentalsData(FundamentalsMessage fundamentalsMessage)
        {
            fundamentals.Text = fundamentalsMessage.Data;
            fundamentalsRequestActive = false;
        }

        public void RequestContractDetails(Contract contract)
        {
            if (!contractRequestActive)
            {
                contractDetailsGrid.Rows.Clear();
                bondContractDetailsGrid.Rows.Clear();
                ibClient.ClientSocket.reqContractDetails(CONTRACT_DETAILS_ID, contract);
            }
        }

        public void RequestFundamentals(Contract contract, string reportType)
        {
            fundamentals.Text = "";
            if (!fundamentalsRequestActive)
            {
                fundamentalsRequestActive = true;
                ibClient.ClientSocket.reqFundamentalData(FUNDAMENTALS_ID, contract, reportType, new List<TagValue>());
            }
            else
            {
                fundamentalsRequestActive = false;
                ibClient.ClientSocket.cancelFundamentalData(FUNDAMENTALS_ID);
            }
        }

        public void RequestMarketDataType(int marketDataType)
        {
            ibClient.ClientSocket.reqMarketDataType(marketDataType);
        }

        public ComboContractResults ComboContractResults
        {
            get { return comboContractResults; }
            set { comboContractResults = value; }
        }

        public IBClient IbClient
        {
            get { return ibClient; }
            set { ibClient = value; }
        }

        public TextBox Fundamentals
        {
            get { return fundamentals; }
            set { fundamentals = value; }
        }

        public DataGridView ContractDetailsGrid
        {
            get { return contractDetailsGrid; }
            set { contractDetailsGrid = value; }
        }

        public DataGridView BondContractDetailsGrid
        {
            get { return bondContractDetailsGrid; }
            set { bondContractDetailsGrid = value; }
        }

        public bool IsComboLegRequest
        {
            get { return isComboLegRequest; }
            set { isComboLegRequest = value; }
        }
    }
}

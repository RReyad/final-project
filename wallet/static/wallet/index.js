document.addEventListener('DOMContentLoaded', function() {

    document.querySelector('#Add_To_Wallet_Form').addEventListener('submit',add_to_wallet);
    document.querySelector('#Transfer_Form').addEventListener('submit',transfer);
    

    display_transactions();
  });
  
  // Dictionary for pie chart categories 
    var category_list_dictionary = ["Remmittance to Friend", "Food", "Fuel", "Utilities", "Rentals", "Others", "Money Receivied"]


   // Function to add add funds to wallet 
function add_to_wallet(){
    
    add_value = document.getElementById('Add_To_Wallet_Input').value
    fetch('/add_to_wallet', {
        method: 'POST',
        body: JSON.stringify({
            amount: add_value,
         })
     })
        .then(response => response.json())
          .then(result => {
              if (result.error) { alert(result.error); }
              else if (result.message) { alert(result.message);}
           
          });

    
}

function transfer(){
      transfer_value = document.getElementById('Transfer_Value_Input').value
      transfer_to = document.getElementById('Transfer_To_Input').value
      transfer_to_description = document.getElementById('Transfer_To_Description').value
      transfer_to_category =document.getElementById('Transfer_To_Category').value
      
     fetch('/transfer_to_wallet', {
        method: 'POST',
        body: JSON.stringify({
            amount: transfer_value,
            transfer_to: transfer_to,
            description: transfer_to_description,
            category: transfer_to_category
            
          })
     })
        .then(response => response.json())
          .then(result => {
              if (result.error) { alert(result.error); }
              else if (result.message) { alert(result.message);}
           
          });

}


function display_transactions(){

      fetch('/balance').then(response => response.json()).then(result => { 
        var wallet_balance = document.getElementById("Wallet");
        wallet_balance.style.fontWeight = "bold";
        wallet_balance.textContent  = ` Balance In Wallet ${ result["Balance"]} USD`;
        });
      
        fetch('/transactions').then(response => response.json()).then(transactions_list=> { 
              
          Table_Id = document.getElementById("Transactions_list")
          for (i=0; i<transactions_list.length; i++){
            var row = Table_Id.insertRow(i+1);
            
            var table_data_0 = row.insertCell(0);
            var table_data_1 = row.insertCell(1);
            var table_data_2 = row.insertCell(2);
            var table_data_3 = row.insertCell(3);
            var table_data_4 = row.insertCell(4);
            var table_data_5 = row.insertCell(5);
            var table_data_6 = row.insertCell(6);

           table_data_0.textContent = transactions_list[i].From;
           table_data_1.textContent = transactions_list[i].To;
           table_data_2.textContent = transactions_list[i].Description;
           table_data_3.textContent = transactions_list[i].Value;
           table_data_4.textContent = transactions_list[i].Type;
           table_data_5.textContent = category_list_dictionary[transactions_list[i].Category];
           table_data_6.textContent = transactions_list[i].Timestamp; 
                        

          } // end of for loop
          monthly_spend = Serialize_List_Monthly(transactions_list);
          monthly_spend_graph(monthly_spend);
          spend_by_category = Serialize_List_Category(transactions_list);
          spend_by_category_graph(spend_by_category); 
          
        }); // end of fetch
      
}//  end pd display Post Function


function Serialize_List_Monthly(input_list){
    var output_list = [0,0,0,0,0,0,0,0,0,0,0,0];
    
    for (i=0; i< input_list.length; i++){
     if(input_list[i].Type == "Debit"){
      transaction_date = new Date(input_list[i].Timestamp);
      transaction_month = transaction_date.getMonth();
      var transaction_value = -parseFloat(input_list[i].Value);

      output_list[transaction_month] = output_list[transaction_month] + transaction_value;
     

     }
        

    }
    
    return output_list;
}

function Serialize_List_Category(input_list){
  var output_list = [0,0,0,0,0,0];
  
  for (i=0; i< input_list.length; i++){
   if(input_list[i].Type == "Debit"){
    transaction_category = input_list[i].Category;
    var transaction_value = -parseFloat(input_list[i].Value);

    output_list[transaction_category] = output_list[transaction_category] + transaction_value;
     } // end of if 
      

  } // end of for loop
  
  return output_list;
}// end of function

function monthly_spend_graph(input_list) {
    new Chart(document.getElementById("bar-chart"), {
      type: 'bar',
      data: {
        labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun","Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        datasets: [
          {
            label: "Monthly Spend USD",
            backgroundColor: ["#3e95cd", "#3e95cd","#3e95cd","#3e95cd","#3e95cd","#3e95cd", "#3e95cd","#3e95cd","#3e95cd","#3e95cd","#3e95cd","#3e95cd" ],
            data: input_list
          }
        ]
      },
      options: {
        legend: { display: false },
        title: {
          display: true,
          text: 'Monthly Spend in USD'
        }
      }
    });
}

function spend_by_category_graph(input_list) {
  new Chart(document.getElementById("pie-chart"), {
    type: 'pie',
    data: {
     // labels:category_list_dictionary,
        datasets: [{
        label: "Spend in USD",
        backgroundColor: ["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850","#c42000" ],
        data: input_list
      }]
    }, // end of labels
    options: {
      title: {
        display: true,
        text: 'Spend By Category'
      }
      
    } // end of options
 }); // end of chart

}


//Donal Tuohy
//
//Messing around with node.js
//Corresponds to the first few thenewboston tutorials
//
var Person = {
    firstName: "Donal",
    secondName: "Tuohy",
    age: 28
};

function addNumber(a, b){
    return a + b;
}

function placeAnOrder(orderNumber){
    console.log("Placed order ", orderNumber);

    cookAndDeliverFood(function (){
        console.log("Completed order ", orderNumber);
    });
}


function cookAndDeliverFood(callBack){
        setTimeout(callBack, 5000);
}

//Simulate database requests
placeAnOrder(1); 
placeAnOrder(2);
placeAnOrder(3);
placeAnOrder(4);


console.log(Person);
console.log(addNumber(3, 7));
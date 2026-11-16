function confirmCancel(){
    return confirm('Are you sure you want to cancel this appointment?');
}

function validateForm(){
    let reason=document.getElementById("reason").value.trim();
    if(reason ===""){
        alert("Please enter a reason.");
        return false;
    }
    return true;
}

setTimeout(function(){
    let msg=document.querySelector(".flash");
    if(msg)
        msg.style.display="none";
},2000);





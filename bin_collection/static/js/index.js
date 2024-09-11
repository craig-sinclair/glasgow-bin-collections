document.addEventListener("DOMContentLoaded", function() {
    document.querySelector('.form-box-div').style.display = 'none';
    document.getElementById('loading-container').style.display = 'flex';

    function checkDriverStatus() {
        fetch(checkDriverStatusUrl)  
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ready') {
                    
                    document.querySelector('.form-box-div').style.display = 'block';
                    document.getElementById('loading-container').style.display = 'none';
                } else {

                    setTimeout(checkDriverStatus, 1000);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }

    checkDriverStatus();
});

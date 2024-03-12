$(document).ready(function () {
    // Fetch IP addresses and update the dropdown
    function populateIPAddresses() {
        $.ajax({
            url: "{% url 'your_endpoint_to_fetch_ip_addresses' %}",
            method: "GET",
            success: function (data) {
                var ipAddressSelect = $("#ipAddressSelect");
                ipAddressSelect.empty();
                ipAddressSelect.append('<option value="">Select IP Address</option>');
                data.ipAddresses.forEach(function (ipAddress) {
                    ipAddressSelect.append('<option value="' + ipAddress + '">' + ipAddress + '</option>');
                });
            },
            error: function (error) {
                console.log(error);
            }
        });
    }

    // Update data in your manual table
    function updateManualTableData(selectedIP, building, lanRoom) {
        $.ajax({
            url: "{% url '/update_manual_table/' %}",
            method: "POST",
            data: {
                selectedIP: selectedIP,
                building: building,
                lanRoom: lanRoom
            },
            success: function (data) {
                // Handle success
            },
            error: function (error) {
                console.log(error);
            }
        });
    }

    // Edit button click event listener for the header
    $(".edit-button-header").on("click", function () {
        // Show the edit popup
        $("#editPopup").modal("show");

        // Clear the previous values from the form
                // Clear the previous values from the form
        $("#ipAddressSelect").val(""); // Reset IP Address select
        $("#building").val("");
        $("#lanRoom").val("");

        // Populate the IP addresses from your data source
        populateIPAddresses();

        // When an IP Address is selected from the dropdown, populate the form
        $("#ipAddressSelect").on("change", function () {
            var selectedIP = $(this).val();
            // You can add more logic here to fetch and populate other fields
        });

        // Handle form submission for editing data
        $("#saveChanges").on("click", function () {
            // Get the values from the form
            var selectedIP = $("#ipAddressSelect").val();
            var building = $("#building").val();
            var lanRoom = $("#lanRoom").val();

            // Update the data in your manual table
            updateManualTableData(selectedIP, building, lanRoom);

            // Close the edit popup
            $("#editPopup").modal("hide");
        });
    });
});


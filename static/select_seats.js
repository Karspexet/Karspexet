function setupSelectSeats(allSeats, takenSeats, pricings) {
    var seats = document.querySelectorAll('.seat'),
        booking = {};

    function selectSeat(event) {
        var seat = event.target.id;
        if (booking.hasOwnProperty(seat)) {
            removeSeat(seat);
        } else {
            addSeat(seat);
        }
    }

    function addSeat(seat) {
        var seatId = seat.replace("seat-", "");
        booking[seat] = {id: seatId, value: null};
        document.querySelector('#' + seat).classList.add('selected-seat');
        renderBooking();
    }

    function removeSeat(seat) {
        var seatId = seat.replace("seat-", "");
        delete booking[seat];
        document.querySelector('#' + seat).classList.remove('selected-seat');
        renderBooking();
    }

    function selectSeatType(event) {
        var target = event.target,
            seatId = target.dataset.id,
            seatType = target.value;
        seatKey = "seat-" + seatId;

        booking[seatKey].value = seatType;
        renderBooking();
    }

    function renderBooking() {
        output = "";
        Object.keys(booking).forEach(function(seatId) {
            output += renderSeatForm(booking[seatId]);
        });

        document.querySelector('#booking').innerHTML = output;
        Array.prototype.forEach.call(
            document.querySelectorAll('#booking select'),
            function (select) { select.addEventListener('change', selectSeatType); }
        );
    }

    function renderSeatForm(seat) {
        var seatId = seat.id,
            seatType = seat.value,
            seatObject = allSeats["seat-" + seatId],
            displayName = seatObject.name,
            pricing = pricings[seatObject.group];

        function option(seatType, selectedSeatType) {
            var selectedString = seatType === selectedSeatType ? " selected" : "";
            return '<option value="' + seatType + '" '+ selectedString + '>' +
                seatType[0].toUpperCase() + seatType.slice(1) +
                ' (' + pricing[seatType] + 'kr)' +
                '</option>';
        }
        return '<div><label>' + displayName + ': ' +
            '<select name="seat_' + seatId + '" data-id="' + seatId + '">' +
            '<option value=""></option>' +
            option('normal', seatType) +
            option('student', seatType) +
            '</select></label></div>';
    }

    Object.keys(allSeats).forEach(function(seat) {
        var element = document.getElementById(seat),
            seatObject = allSeats[seat];
        element.addEventListener('mouseover', function() {
            var pricing = pricings[seatObject.group],
                info = '<div>' + seatObject.name + '<br>' +
                'Student: ' + pricing['student'] + 'kr' + '<br>' +
                'Normal: ' + pricing['normal'] + 'kr' + '<br>' +
                '</div>';

            document.querySelector('.seat-info').innerHTML = info;
        });

        element.addEventListener('mouseout', function() {
            document.querySelector('.seat-info').innerHTML = "";
        });
    });

    Array.prototype.forEach.call(
        document.querySelectorAll('.seat:not(.taken-seat)'),
        function makeSeatAvailable(seat) {seat.addEventListener('click', selectSeat);}
    );
}

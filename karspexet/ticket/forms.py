from django import forms

class SeatSelectorForm(forms.Form):
    seat_select = forms.ModelMultipleChoiceField(queryset=None)

    def __init__(self, seating_group):
        super().__init__()
        self.fields['seat_select'].queryset = seating_group.seat_set.all()

class SeatingGroupFormSet():
    def __init__(self, seating_group, taken_seats):
        self.seating_group = seating_group
        self.taken_seats = taken_seats

    @property
    def forms(self):
        return [
            TicketTypeForm(seat, self.taken_seats)
            for seat
            in self.seating_group.seat_set.all()
        ]

class TicketTypeForm(forms.Form):
    def __init__(self, seat, taken_seats):
        super().__init__()
        field_name = "seat_%d" % seat.id
        self.seat_id = seat.id
        self.taken_seats = taken_seats
        self.fields[field_name] = forms.ChoiceField(
            choices=[("student", "Student"), ("normal", "Fullpris")],
            widget=forms.RadioSelect,
            required=False,
            label=seat.name,
        )
        if self.seat_id in self.taken_seats:
            self.fields[field_name].widget.attrs["disabled"] = "disabled"

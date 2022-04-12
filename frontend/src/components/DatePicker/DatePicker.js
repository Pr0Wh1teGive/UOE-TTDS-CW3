import "./DatePicker.css"
import React from "react";
import moment from 'moment';
import DayPickerInput from 'react-day-picker/DayPickerInput';
import 'react-day-picker/lib/style.css';
import { formatDate, parseDate } from 'react-day-picker/moment';

const currentYear = new Date().getFullYear();
const fromMonth = new Date(currentYear-6,0);
const toMonth = new Date();

function YearMonthForm({ date, localeUtils, onChange }) {
    const months = localeUtils.getMonths();

    const years = [];
    for (let i = fromMonth.getFullYear(); i <= toMonth.getFullYear(); i += 1) {
        years.push(i);
    }

    const handleChange = function handleChange(e) {
        const { year, month } = e.target.form;
        onChange(new Date(year.value, month.value));
    };

    return (
        <form className="DayPicker-Caption">
            <select name="month" onChange={handleChange} value={date.getMonth()}>
                {months.map((month, i) => (
                    <option key={month} value={i}>
                        {month}
                    </option>
                ))}
            </select>
            <select name="year" onChange={handleChange} value={date.getFullYear()}>
                {years.map(year => (
                    <option key={year} value={year}>
                        {year}
                    </option>
                ))}
            </select>
        </form>
    );
}

export default class DatePicker extends React.Component {
    constructor(props) {
        super(props);
        this.handleFromChange = this.handleFromChange.bind(this);
        this.handleToChange = this.handleToChange.bind(this);
        this.handleYearMonthChange = this.handleYearMonthChange.bind(this);
        this.state = {
            dateFrom: undefined,
            dateTo: undefined,
            month: new Date(),
        };
    }

    showFromMonth() {
        const { dateFrom, dateTo } = this.state;
        if (!dateFrom) {
            return;
        }
        if (moment(dateTo).diff(moment(dateFrom), 'months') < 2) {
            this.dateTo.getDayPicker().showMonth(dateFrom);
        }
    }

    handleFromChange(dateFrom) {
        this.setState({dateFrom} );
        console.log(dateFrom);
    }

    handleToChange(dateTo) {
        this.setState({ dateTo }, this.showFromMonth);
        console.log(dateTo);
        // pass the date inputted by user to component AdvancedSearch
        this.props.getDate(this.state.dateFrom.toLocaleDateString(), dateTo.toLocaleDateString());
    }

    handleYearMonthChange(month) {
        this.setState({ month });
        console.log(month, fromMonth, toMonth)
    }

    render() {
        const { dateFrom, dateTo } = this.state;
        // const { dateFrom, dateTo } = this.props;
        const modifiers = { start: dateFrom, end: dateTo };

        return (
            <div className="InputFromTo">
                <DayPickerInput
                    //showOverlay={true}
                    value={dateFrom}
                    placeholder="From"
                    format="LL"
                    formatDate={formatDate}
                    parseDate={parseDate}
                    dayPickerProps={{
                        month: this.state.month, // The month to display in the calendar
                        fromMonth: fromMonth, // The first allowed month

                        selectedDays: [dateFrom, { dateFrom, dateTo }],
                        disabledDays: { after: dateTo },
                        toMonth: toMonth, // The last allowed month
                        modifiers,
                        numberOfMonths: 2,
                        onDayClick: () => this.dateTo.getInput().focus(),

                        captionElement: ({ date, localeUtils }) => (
                            <YearMonthForm
                                date={date}
                                localeUtils={localeUtils}
                                onChange={this.handleYearMonthChange}
                            />
                        ),
                    }
                    }
                    onDayChange={this.handleFromChange}
                />
                <span className="InputFromTo-to">
                    <DayPickerInput
                        ref={el => (this.dateTo = el)}
                        value={dateTo}
                        placeholder="To"
                        format="LL"
                        formatDate={formatDate}
                        parseDate={parseDate}
                        dayPickerProps={{
                            toMonth: toMonth,
                            month:this.state.month,

                            selectedDays: [dateFrom, { dateFrom, dateTo }],
                            disabledDays: { before: dateFrom },
                            modifiers,
                            // month: dateFrom,
                            fromMonth: dateFrom,
                            numberOfMonths: 2,

                            captionElement: ({ date, localeUtils }) => (
                                <YearMonthForm
                                    date={date}
                                    localeUtils={localeUtils}
                                    onChange={this.handleYearMonthChange}
                                />
                            ),
                        }}
                        onDayChange={this.handleToChange}
                    />
                </span>
            </div>
        );
    }
}

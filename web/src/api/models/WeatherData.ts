/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Response model for weather data records
 */
export type WeatherData = {
    id: number;
    dateutc: number;
    date: string;
    tempf?: (number | null);
    feelsLike?: (number | null);
    dewPoint?: (number | null);
    tempinf?: (number | null);
    humidity?: (number | null);
    humidityin?: (number | null);
    baromrelin?: (number | null);
    baromabsin?: (number | null);
    windspeedmph?: (number | null);
    windgustmph?: (number | null);
    winddir?: (number | null);
    maxdailygust?: (number | null);
    hourlyrainin?: (number | null);
    dailyrainin?: (number | null);
    weeklyrainin?: (number | null);
    monthlyrainin?: (number | null);
    totalrainin?: (number | null);
    solarradiation?: (number | null);
    uv?: (number | null);
    battout?: (number | null);
    battin?: (number | null);
    raw_json?: (string | null);
};


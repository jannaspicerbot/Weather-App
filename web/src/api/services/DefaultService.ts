/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DatabaseStats } from '../models/DatabaseStats';
import type { WeatherData } from '../models/WeatherData';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DefaultService {
    /**
     * Read Root
     * Root endpoint with API information
     * @returns any Successful Response
     * @throws ApiError
     */
    public static readRootGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/',
        });
    }
    /**
     * Get Weather Data
     * Query weather data from the database
     *
     * Parameters:
     * - limit: Maximum number of records (1-1000, default: 100)
     * - offset: Number of records to skip (for pagination)
     * - start_date: Filter by start date (YYYY-MM-DD format)
     * - end_date: Filter by end date (YYYY-MM-DD format)
     * - order: Sort order - 'asc' or 'desc' (default: desc)
     * @param limit Maximum number of records to return
     * @param offset Number of records to skip
     * @param startDate Start date (ISO format: YYYY-MM-DD)
     * @param endDate End date (ISO format: YYYY-MM-DD)
     * @param order Sort order by date (asc or desc)
     * @returns WeatherData Successful Response
     * @throws ApiError
     */
    public static getWeatherDataWeatherGet(
        limit: number = 100,
        offset?: number,
        startDate?: (string | null),
        endDate?: (string | null),
        order: string = 'desc',
    ): CancelablePromise<Array<WeatherData>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/weather',
            query: {
                'limit': limit,
                'offset': offset,
                'start_date': startDate,
                'end_date': endDate,
                'order': order,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Latest Weather
     * Get the most recent weather data reading
     * @returns WeatherData Successful Response
     * @throws ApiError
     */
    public static getLatestWeatherWeatherLatestGet(): CancelablePromise<WeatherData> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/weather/latest',
        });
    }
    /**
     * Get Database Stats
     * Get statistics about the weather database
     * @returns DatabaseStats Successful Response
     * @throws ApiError
     */
    public static getDatabaseStatsWeatherStatsGet(): CancelablePromise<DatabaseStats> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/weather/stats',
        });
    }
    /**
     * Health Check
     * Health check endpoint for monitoring
     * @returns any Successful Response
     * @throws ApiError
     */
    public static healthCheckApiHealthGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/health',
        });
    }
    /**
     * Api Get Latest Weather
     * Get the latest weather readings (API route)
     * @param limit
     * @returns any Successful Response
     * @throws ApiError
     */
    public static apiGetLatestWeatherApiWeatherLatestGet(
        limit: number = 100,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/weather/latest',
            query: {
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Api Get Weather Range
     * Get weather data within a date range (API route)
     * @param startDate
     * @param endDate
     * @param limit
     * @returns any Successful Response
     * @throws ApiError
     */
    public static apiGetWeatherRangeApiWeatherRangeGet(
        startDate?: (string | null),
        endDate?: (string | null),
        limit: number = 1000,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/weather/range',
            query: {
                'start_date': startDate,
                'end_date': endDate,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Api Get Stats
     * Get database statistics (API route)
     * @returns any Successful Response
     * @throws ApiError
     */
    public static apiGetStatsApiWeatherStatsGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/weather/stats',
        });
    }
}

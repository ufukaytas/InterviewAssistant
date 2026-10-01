using System;
using System.Collections.Generic;
using System.Text;
using System.Text.Json.Serialization;

namespace Auth.Application.DTOs
{
    public class CustomResponseDto<T>
    {
        public T? Data { get; set; }
        public bool IsSuccessfull { get; set; }
        public string? Message { get; set; }
        public List<string>? Errors { get; set; }


        [JsonIgnore]
        public int StatusCode { get; set; }

        //Başarılı ve geriye veri dönen 
        public static CustomResponseDto<T> Success(int statusCode, T data, string message = null)
        {
            return new CustomResponseDto<T>
            {
                Data = data,
                Message = message,
                StatusCode = statusCode,
                IsSuccessfull = true
            };
        }

        //Başarılı fakat geriye veri dönmeyen
        public static CustomResponseDto<T> Success(int statusCode, string message = null)
        {
            return new CustomResponseDto<T>
            {
                Message = message,
                StatusCode = statusCode,
                IsSuccessfull = true
            };
        }

        //Başarısız ve geriye birden fazla hata dönen
        public static CustomResponseDto<T> Fail(int statusCode, List<string> errors, string message = "İşlem sırasında hatalar oluştu")
        {
            return new CustomResponseDto<T>
            {
                Errors = errors,
                Message = message,
                StatusCode = statusCode,
                IsSuccessfull = false
            };
        }

        // Başarısız ve geriye tek bir hata dönen
        public static CustomResponseDto<T> Fail(int statusCode, string error, string message = "İşlem sırasında hata oluştu")
        {
            return new CustomResponseDto<T>
            {
                Errors = new List<string> { error },
                Message = message,
                StatusCode = statusCode,
                IsSuccessfull = false
            };
        }
    }

    // non-generic veri dönmeyen işlemleri için (Create, Update, Delete)
    public class CustomResponseDto
    {
        public string? data { get; set; }
        public bool IsSuccessfull { get; set; }
        public string? Message { get; set; }
        public List<string>? Errors { get; set; }
        [JsonIgnore]
        public int StatusCode { get; set; }

        public static CustomResponseDto Success(int statusCode, string message = null)
        {
            return new CustomResponseDto
            {
                IsSuccessfull = true,
                Message = message,
                StatusCode = statusCode
            };
        }

        public static CustomResponseDto Success(int statusCode, string orderNumber, string message = null)
        {
            return new CustomResponseDto
            {
                data = orderNumber,
                IsSuccessfull = true,
                Message = message,
                StatusCode = statusCode
            };
        }

        public static CustomResponseDto Fail(int statusCode, List<string> errors, string message = "İşlem sırasında hatalar oluştu")
        {
            return new CustomResponseDto
            {
                IsSuccessfull = false,
                Message = message,
                Errors = errors,
                StatusCode = statusCode
            };
        }
        public static CustomResponseDto Fail(int statusCode, string error, string message = "İşlem sırasında hata oluştu")
        {
            return new CustomResponseDto
            {
                IsSuccessfull = false,
                Message = message,
                Errors = new List<string> { error },
                StatusCode = statusCode
            };
        }
    }
}

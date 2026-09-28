using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Application.Exceptions
{
    public class ValidationException : Exception
    {
        public IDictionary<string, string[]> Errors { get; }

        public ValidationException(IDictionary<string, string[]> errors) : base("Doğrulama hataları oluştu")
        {
            Errors = errors;
        }
    }
}

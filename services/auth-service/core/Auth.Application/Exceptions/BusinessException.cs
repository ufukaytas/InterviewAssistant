using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Application.Exceptions
{
    public class BusinessException : Exception
    {
        public BusinessException(string? message) : base(message)
        {
        }
    }
}

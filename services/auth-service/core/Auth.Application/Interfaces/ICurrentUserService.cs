using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Application.Interfaces
{
    public interface ICurrentUserService
    {
        string? UserId { get; }
    }
}

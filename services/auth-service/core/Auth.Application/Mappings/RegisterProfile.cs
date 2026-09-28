using Auth.Application.Features.Auth.Commands.Register;
using Auth.Domain.Entities;
using AutoMapper;
using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Application.Mappings
{
    public class RegisterProfile:Profile
    {
        public RegisterProfile()
        {
            CreateMap<RegisterCommandRequest, User>();
        }
    }
}

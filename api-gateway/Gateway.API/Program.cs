using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;
using System.Security.Claims;
using System.IdentityModel.Tokens.Jwt;
using System.Text;
using Yarp.ReverseProxy.Transforms;

var builder = WebApplication.CreateBuilder(args);

// Sub claim'ini bozmaması için
JwtSecurityTokenHandler.DefaultInboundClaimTypeMap.Clear();

// x. JWT ayarlarını oku
var jwtSettings = builder.Configuration.GetSection("JwtSettings");
var secretKey = jwtSettings["Key"];

// y. Authentication servisini ekliyoruz
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidIssuer = jwtSettings["Issuer"],
            ValidateAudience = true,
            ValidAudience = jwtSettings["Audience"],
            ValidateIssuerSigningKey = true,
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secretKey)),
            ValidateLifetime = true
        };
    });

// z. Authorization ekledim
builder.Services.AddAuthorization();

// a. CORS AYARLARI (React UI'dan gelen isteklere izin veriyoruz)
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowReactUI", policy =>
    {
        // UI'ın adresi
        policy.WithOrigins("https://localhost:3011", "http://localhost:3011")
        .AllowAnyHeader()
        .AllowAnyMethod();
    });
});

// b. YARP AYARLARI (Reverse Proxy'yi ve appsettings'teki kuralları yüklüyoruz) ve X-User-Id Transformunu yazıyoruz
builder.Services.AddReverseProxy()
    .LoadFromConfig(builder.Configuration.GetSection("ReverseProxy"))
    .AddTransforms(builderContext =>
    {
        builderContext.AddRequestTransform(transformContext =>
        {
            // eğer istek yapan kullanıcı giriş yapmışsa (token doğrulanmışsa)
            if (transformContext.HttpContext.User.Identity?.IsAuthenticated == true)
            {
                var userId = transformContext.HttpContext.User.FindFirst(JwtRegisteredClaimNames.Sub)?.Value;

                if (!string.IsNullOrEmpty(userId))
                {
                    // Arkadaki mikroservise X-User-Id header'ı olarak ekle
                    transformContext.ProxyRequest.Headers.Add("X-User-Id", userId);
                }
            }
            return ValueTask.CompletedTask;
        });
    });

// Add services to the container.

builder.Services.AddControllers();
// Learn more about configuring OpenAPI at https://aka.ms/aspnet/openapi
builder.Services.AddOpenApi();

var app = builder.Build();

app.UseRouting();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
}

app.UseHttpsRedirection();

app.UseCors("AllowReactUI");

app.UseAuthentication();
app.UseAuthorization();


// c. YARP'ın trafik yönlendirme mekanizmasını çalıştırıyoruz.
app.MapReverseProxy();

app.MapControllers();

app.Run();

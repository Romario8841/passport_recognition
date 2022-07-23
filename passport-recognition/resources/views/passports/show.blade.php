<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>Laravel</title>

    <!-- Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap" rel="stylesheet">

    <style>
        body {
            font-family: 'Nunito';
        }
    </style>
</head>
<body>
<!-- if validation in the controller fails, show the errors -->
@if ($errors->any())
    <div class="alert alert-danger">
        <ul>
            @foreach ($errors->all() as $error)
                <li>{{ $error }}</li>
            @endforeach
        </ul>
    </div>
@endif

<div>
        <h1>Data:
            @if($passport->on_pending)
                Обработка...
                <script>

                    function timedRefresh(timeoutPeriod) {
                        setTimeout("location.reload(true);",timeoutPeriod);
                    }

                    window.onload = timedRefresh(5000);

                </script>

            @else

                {{ $passport->first_name}}
            @endif


        </h1>
</div>
</body>
</html>

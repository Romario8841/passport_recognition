<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class Passport extends Model
{
    use HasFactory;

    use HasFactory;
    public mixed $passports;
    /**
     * @var mixed|string
     */

    protected $table = 'passports';
    # Разрешение на изменение данных в таблице
    protected $guarded  = [];
}

<?php

namespace App\Http\Controllers;

use App\Http\Requests\StoreRequest;
use App\Jobs\ProcessPassportScanJob;
use App\Models\Passport;
use Illuminate\Contracts\Foundation\Application;
use Illuminate\Contracts\View\Factory;
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Illuminate\Support\Facades\DB;
use Symfony\Component\Process\Process;
use Symfony\Component\Process\Exception\ProcessFailedException;

class PassportController extends Controller
{
    /**
     * Display a listing of the resource.
     *
     * @return Response
     */

    /**
     * Show the form for creating a new resource.
     *
     * @return Application|Factory|\Illuminate\Contracts\View\View
     */
    public function create(): \Illuminate\Contracts\View\View|Factory|Application
    {
        return view('passports.create');
    }

    /**
     * Store a newly created resource in storage.
     *
     * @param Request $request
     * @return void
     */

    public function store(Request $request)
    {
        // ensure the request has a file before we attempt anything else.
        if ($request->hasFile('file')) {

            $request->validate([
                'image' => 'mimes:jpeg,bmp,png' // Only allow .jpg, .bmp and .png file types.
            ]);

            // Save the file locally in the storage/public/ folder under a new folder named /product
            $request->file->store('passports', 'public');


            $file_path = "storage\app\public\passports\\" . $request->file->hashName();
            // Store the record, using the new file hashname which will be it's new filename identity.

            $passport = new Passport;
            $passport->file_path = $file_path;
            $passport->on_pending = true;
            $passport->save();
            dispatch(new ProcessPassportScanJob($file_path, $passport));

            return redirect()->route('show', $passport->id);
        }
    }

        public function show($id)
        {
            Passport::all();
            $passport = Passport::where('id', $id)->first();
            return view('passports.show', compact('passport'));


//            return view('passports.show', compact($data));

        }



}
